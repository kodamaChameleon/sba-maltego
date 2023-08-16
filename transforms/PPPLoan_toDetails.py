import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry,sba_set
from modules import ckan, naics

# Attempt to distinguish between a person's name and an Company
def classify_name(name):
    # List of common Company-related words and keywords
    Company_keywords = ["inc", "inc.", "corp", "corp." "company", "group", "foundation", "llc", "l.l.c." "ltd", "llp", "co", "co.", "corporation"]

     # Split the name by spaces
    name_parts = name.lower().split(' ')

    # Assume names of people will not be greater than 4 parts
    if len(name_parts) > 4:
        return "Company"

    # Test final naming part for Company keywords
    for keyword in Company_keywords:
        if keyword == name_parts[-1]:
            return "Company"

    return "Person"


@registry.register_transform(
    display_name="PPP Loan Details [SBA]", 
    input_entity="maltego.UniqueIdentifier",
    description='Extrapolate details of PPP loan',
    settings=[],
    output_entities=["maltego.Unknown"],
    transform_set=sba_set
)
class PPPLoan_toDetails(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        async def main():

            data = ckan.dataset("ppp-foia")
            search_terms = {
                "LoanNumber": request.Value
            }

            results = data.get_rows(search_terms)

            for x in range(len(results.index)):
                date_approved = response.addEntity("maltego.DateTime", value = results.loc[x, 'DateApproved'])
                date_approved.setLinkLabel("Date Approved")

                borrower_name = response.addEntity("maltego." + classify_name(results.loc[x, 'BorrowerName']), value = results.loc[x, 'BorrowerName'])
                borrower_name.setLinkLabel("Borrower")

                if results.loc[x, 'BorrowerAddress'] not in ("N/A", None):
                    borrower_location = response.addEntity("maltego.Location")
                    borrower_location.addProperty("streetaddress", value = results.loc[x, 'BorrowerAddress'])
                    borrower_location.addProperty("country", value = "United States")
                    borrower_location.addProperty("city", value = results.loc[x, 'BorrowerCity'])
                    borrower_location.addProperty("location.area", value = results.loc[x, 'BorrowerState'])
                    borrower_location.addProperty("location.areacode", value = results.loc[x, 'BorrowerZip'])
                    borrower_location.addProperty("countrycode", value = "US")
                    borrower_location.setLinkLabel("Borrower's Address")

                loan_amount = response.addEntity("maltego.Phrase", value = "$" + str(results.loc[x, 'CurrentApprovalAmount']))
                loan_amount.setLinkLabel("Amount")

                if results.loc[x, 'FranchiseName'] not in ("N/A", None):
                    franchise_name = response.addEntity("maltego.Company", value = results.loc[x, 'FranchiseName'])
                    franchise_name.setLinkLabel("Franchise")

                lender_name = response.addEntity("maltego.Company", value = results.loc[x, 'ServicingLenderName'])
                lender_name.setLinkLabel("Lender")

                if results.loc[x, 'ServicingLenderAddress'] not in ("N/A", None):
                    lender_location = response.addEntity("maltego.Location")
                    lender_location.addProperty("streetaddress", value = results.loc[x, 'ServicingLenderAddress'])
                    lender_location.addProperty("country", value = "United States")
                    lender_location.addProperty("city", value = results.loc[x, 'ServicingLenderCity'])
                    lender_location.addProperty("location.area", value = results.loc[x, 'ServicingLenderState'])
                    lender_location.addProperty("location.areacode", value = results.loc[x, 'ServicingLenderZip'])
                    lender_location.addProperty("countrycode", value = "US")
                    lender_location.setLinkLabel("Lender's Address")

                if results.loc[x, 'BusinessAgeDescription'] not in ("N/A", None, "Unanswered"):
                    business_age = response.addEntity("maltego.Phrase", value = results.loc[x, 'BusinessAgeDescription'])
                    business_age.setLinkLabel("Business Age")

                if  results.loc[x, 'BusinessType']:
                    response.addEntity("maltego.Industry", value = results.loc[x, 'BusinessType'])

                if results.loc[x, 'NAICSCode']:
                    industry_type = response.addEntity("maltego.Industry", value = naics.get_industry(results.loc[x, 'NAICSCode']))
                    industry_type.addProperty("naics", value = results.loc[x, 'NAICSCode'])

                if results.loc[x, 'Race'] not in (None, "Unanswered"):
                    race = response.addEntity("maltego.hashtag", value = results.loc[x, 'Race'])
                    race.addProperty("Category", value = "Race")

                if results.loc[x, 'Ethnicity'] not in (None, "Unknown/NotStated"):
                    race = response.addEntity("maltego.hashtag", value = results.loc[x, 'Ethnicity'])
                    race.addProperty("Category", value = "Ethnicity")

                if results.loc[x, 'Gender'] not in (None, "Unanswered"):
                    gender = response.addEntity("maltego.hashtag", value = results.loc[x, 'Gender'])
                    gender.addProperty("Category", value = "Gender")

                if results.loc[x, 'Veteran'] not in (None, "Unanswered"):
                    veteran_status = response.addEntity("maltego.hashtag", value = results.loc[x, 'Veteran'])
                    veteran_status.addProperty("Category", value = "Veteran Status")


        trio.run(main)  # running our async code in a non-async code