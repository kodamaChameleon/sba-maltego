import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry,sba_set
from modules import ckan

@registry.register_transform(
    display_name="Get PPP Loans [SBA]", 
    input_entity="maltego.Location",
    description='Returns loan number from location by borrower',
    settings=[],
    output_entities=["maltego.UniqueIdentifier"],
    transform_set=sba_set
)
class PPPLoan_fromBorrowingAddress(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        async def main():

            data = ckan.dataset("ppp-foia")
            search_terms = {
                "BorrowerAddress": request.getProperty('streetaddress'),
                "BorrowerCity": request.getProperty('city'),
                "BorrowerState": request.getProperty('area'),
                "BorrowerZip": request.getProperty('location.areacode')
            }

            results = data.get_rows(search_terms)

            for x in range(len(results.index)):
                loan_entity = response.addEntity("maltego.UniqueIdentifier", value = results.loc[x, 'LoanNumber'])
                loan_entity.addProperty("identifierType", value = "PPP Loan Number")


        trio.run(main)  # running our async code in a non-async code