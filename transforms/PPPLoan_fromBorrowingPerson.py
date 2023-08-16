import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry,sba_set
from modules import ckan

@registry.register_transform(
    display_name="Get PPP Loans [SBA]", 
    input_entity="maltego.Person",
    description='Returns loan number from name by borrower',
    settings=[],
    output_entities=["maltego.UniqueIdentifier"],
    transform_set=sba_set
)
class PPPLoan_fromBorrowingPerson(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        async def main():

            full_name = request.Value

            # If firstname lastname, add % for missing middle names/initials
            name_part = full_name.split(' ')
            if len(name_part) == 2:
                full_name = name_part[0] + " % " + name_part[1]

            data = ckan.dataset("ppp-foia")
            search_terms = {
                "BorrowerName": full_name
            }

            results = data.get_rows(search_terms)

            for x in range(len(results.index)):
                loan_entity = response.addEntity("maltego.UniqueIdentifier", value = results.loc[x, 'LoanNumber'])
                loan_entity.addProperty("identifierType", value = "PPP Loan Number")


        trio.run(main)  # running our async code in a non-async code