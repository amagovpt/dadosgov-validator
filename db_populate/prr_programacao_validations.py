from app.models import ValidationRuleset
from app import create_app, db


TITLE = "PRR Programação - Regras de Validação"
DESCRIPTION = ""
DADOSGOV_DATASET_ID = None

"""
================================================================================================================
INVESTIMENTOS
================================================================================================================
"""
investimentos_dataset_id = "6718cb20d7c1ce7589c5008c"
investimentos_resource_id = "6718cb20d7c1ce7589c5008c"

"""
###############################################################################################
DB INTERACTION 
###############################################################################################
"""

DADOSGOV_RESOURCE_ID_LIST = [

]
ALL_RULES = []


def main():
    app = create_app()

    with app.app_context():
        validation_ruleset = ValidationRuleset(
            title=TITLE,
            description=DESCRIPTION,
            dadosgov_dataset_id=DADOSGOV_DATASET_ID,
            dadosgov_resource_id_list=DADOSGOV_RESOURCE_ID_LIST,
            rules=ALL_RULES
        )

        db.session.add(validation_ruleset)
        db.session.commit()


if __name__ == "__main__":
    main()