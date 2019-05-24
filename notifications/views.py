from random import randint
from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from .models import Notification
from .tasks import send_sms

from registrations.utils import ExtendedTools
from fund_transfers.models import FundTransfer
from registrations.models import Account, Accountant


class NotificationOTP(ExtendedTools, views.APIView):
    """
    Generates OTP, saves it to FT, sends it by SMS and returns status only
    """
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def generate_otp(fund_transfer):
        otp = randint(1, 1000000)
        otp = f'{otp:06d}'

        fund_transfer.otp_generated = otp
        fund_transfer.save()
        return otp

    def get(self, request, transfer_pk):

        extended_user = self.get_extended_user(request.user)
        fund_transfer = self.get_object_or_err(model_object=FundTransfer, pk=transfer_pk)

        if Account.objects.filter(pk=fund_transfer.account.pk).filter(users__pk=request.user.pk).exists()\
                and not isinstance(extended_user, Accountant):

            # Generate OTP
            otp = self.generate_otp(fund_transfer)

            # Save to FT
            fund_transfer.otp_generated = otp
            fund_transfer.save()

            # Send by SMS
            notification = Notification(type='S', to=extended_user.mobile_phone,
                                        contents=f' OTP: {otp} for Fund Transfer {transfer_pk}')
            send_sms(to_phone_number=notification.to, message_body=notification.contents)
            notification.status = 'S'
            notification.save()

            return Response(status=HTTP_200_OK)

        return Response(status=HTTP_400_BAD_REQUEST)
