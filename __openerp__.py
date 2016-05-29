{
    'name': 'Colombia - Terceros',
    'category': 'Localization',
    'version': '0.9',
    'author': 'Dominic Krimmer, Plastinorte S.A.S',
    'maintainer': 'dominic.krimmer@gmail.com',
    'website': 'https://www.plastinorte.com',
    'license': 'AGPL',
    'summary': 'Colombia Terceros: Extended Partner Module - Odoo 9.0',
    'description': """
Colombia Terceros:
======================

    * Redesign of the contact form due to some new rules that have to apply
    * Additional fields: first and second name, first and second last name
    * Additional fields: Document Type, Document Number and Types, Tributate regime, CIIU
    * Automatic Verification of NIT (DV)
    * Interface to maintain the list of CIIU
    * Contacts can be found using Identification Number (e.g. NIT)
    * Country -> State -> Municipality - Logic to avoid confusion of locations with same names
    * "Identification <-> Document Type" - Combination will be checked as this combination should be unique

    """,
    'depends': [
        'account',
        'account_accountant',
        'base'
    ],
    'data': [
        'views/l10n_co_res_partner.xml',
        'views/ciiu.xml',
        'data/ciiu.csv',
        'data/l10n_states_co_data.xml',
        'data/l10n_cities_co_data.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}