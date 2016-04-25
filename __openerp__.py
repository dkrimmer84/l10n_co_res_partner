{
    'name': 'Colombia - Partner Information',
    'category': 'Localization',
    'version': '0.2',
    'author': 'Dominic Krimmer, Plastinorte S.A.S',
    'maintainer': 'dominic.krimmer@gmail.com',
    'website': 'https://www.plastinorte.com',
    'description': """
Colombian Partner Rules:
======================

    * Additional fields: first and second name, first and second last name
    * Additional fields: Document Type, Document Number & Tributate regime
    * CIIU, ICA y CREE ...
    """,
    'depends': [
        'account',
        'account_accountant',
        'base',
    ],
    'data': [
        'views/l10n_co_res_partner.xml',
        'views/ciiu.xml'
    ],
    'installable': True,
}