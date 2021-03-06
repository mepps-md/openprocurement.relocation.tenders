# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    APIResource,
    ROUTE_PREFIX,
    context_unpack
)
from openprocurement.tender.core.utils import save_tender, optendersresource
from openprocurement.relocation.core.utils import change_ownership
from openprocurement.relocation.core.validation import validate_ownership_data
from openprocurement.relocation.tenders.validation import validate_tender_bid_accreditation_level


@optendersresource(name='Bid ownership',
                   path='/tenders/{tender_id}/bids/{bid_id}/ownership',
                   description="Bid Ownership")
class BidResource(APIResource):

    @json_view(permission='create_bid',
               validators=(validate_tender_bid_accreditation_level,
                           validate_ownership_data,))
    def post(self):
        bid = self.request.context
        tender = self.request.validated['tender']
        location = self.request.route_path('{}:Tender Bids'.format(tender['procurementMethodType']), tender_id=tender.id, bid_id=bid.id)
        location = location[len(ROUTE_PREFIX):]  # strips /api/<version>

        if change_ownership(self.request, location) and save_tender(self.request):
            self.LOGGER.info('Updated bid {} ownership of tender {}'.format(bid.id, tender.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'bid_ownership_update'}, {'bid_id': bid.id, 'tender_id': tender.id}))

            return {'data': bid.serialize('view')}
