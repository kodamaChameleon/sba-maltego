import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry,sba_set
from modules import ckan

# Broaden scope of possible name results
def transform_name(name):
    parts = name.split()
    transformed_name = name

    # Check if there are initials (names with more than one part)
    if len(parts) > 2:
        new_name_parts = []
        for part in parts:
            if (len(part) == 1 and part != '%') or (len(part) == 2 and part[1] == '.'):
                new_name_parts.append(part[0] + '%')
            else:
                new_name_parts.append(part)
        transformed_name = ' '.join(new_name_parts)

    elif len(parts) == 2:
        transformed_name = f'{parts[0]}% {parts[1]}'

    return transformed_name

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

            data = ckan.dataset("ppp-foia")
            search_terms = {
                "BorrowerName": transform_name(request.Value)
            }

            results = data.get_rows(search_terms)

            for x in range(len(results.index)):
                loan_entity = response.addEntity("maltego.UniqueIdentifier", value = results.loc[x, 'LoanNumber'])
                loan_entity.addProperty("identifierType", value = "PPP Loan Number")


        trio.run(main)  # running our async code in a non-async code