# -*- coding: utf-8 -*-

# Partner Information App
from openerp import models, fields, api, exceptions

# Extend the Partner Model with some more fields


class PartnerInfoExtended(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # Creating new strings

    # Basic Fields
    PRIMARY_FNAME = "Primer Nombre"
    SECONDARY_FNAME = "Segundo Nombre"
    PRIMARY_NAME = "Primer Apellido"
    SECONDARY_NAME = "Segundo Apellido"
    DOCTYPE = "Tipo de identificación"

    # El numero es el código que la DIAN le asigna a cada uno de esas categorías
    DOCNUM = "Numero de Documento"
    DOCTYPE1 = "13 - Cédula de ciudadanía"
    DOCTYPE2 = "22 - Cédula de extranjería"
    DOCTYPE3 = "31 - NIT (Número de identificación tributaria)"
    DOCTYPE4 = "12 - Tarjeta de identidad"
    DOCTYPE5 = "21 - Tarjeta de extranjería"
    DOCTYPE6 = "41 - Pasaporte"
    DOCTYPE7 = "42 - Documento de identificación extranjero"
    DOCTYPE8 = "43 - Sin identificación del exterior o para uso definido por la DIAN"
    DOCTYPE9 = "11 - Registro civil de nacimiento"

    # Regímen Tributario
    RETRI = "Regímen Tributario"
    RETRI1 = "Simplificado"
    RETRI2 = "P/Natural Común"
    RETRI3 = "Común"
    RETRI4 = "Gran Contribuyente  Auto-retenedor"
    RETRI5 = "Internacional"
    RETRI6 = "Común Auto-retenedor"
    RETRI7 = "Gran Contribuyente"

    # Name field will be replaced
    NAME = "Nombre completo"

    # CIIU
    CIIU = "Actividad CIIU"
    NATURAL = "natural"
    COMPANY = "juridica"
    PERSONTYPE = "Tipo de persona"

    # Company Name
    COMPNAME = "Nombre de la compañia"

    # --- Creating new fields --

    # Company Name
    companyName = fields.Char(COMPNAME)

    # companyType
    companyType = fields.Selection(related='company_type')

    # Replace the name field
    name = fields.Char(
        string=NAME,
        store=True,
        compute="_concat_name",
        required=True
    )

    # Adding new name fields
    x_pn_nombre1 = fields.Char(PRIMARY_FNAME)
    x_pn_nombre2 = fields.Char(SECONDARY_FNAME)
    x_pn_apellido1 = fields.Char(PRIMARY_NAME)
    x_pn_apellido2 = fields.Char(SECONDARY_NAME)

    # Document information
    x_pn_tipoDocumento = fields.Selection(
        [
            (11, DOCTYPE9),
            (12, DOCTYPE4),
            (13, DOCTYPE1),
            (21, DOCTYPE5),
            (22, DOCTYPE2),
            (31, DOCTYPE3),
            (41, DOCTYPE6),
            (42, DOCTYPE7),
            (43, DOCTYPE8)
        ], DOCTYPE
    )
    x_pn_numeroDocumento = fields.Integer(DOCNUM, size=25)
    verificationDigit = fields.Integer('DV', size=2)
    formatedNit = fields.Char(
        string='NIT Formateado',
        compute="_concat_nit",
        store=True
    )

    # Tributate regime
    x_pn_retri = fields.Selection(
        [
            (6, RETRI1),
            (23, RETRI2),
            (7, RETRI3),
            (11, RETRI4),
            (22, RETRI5),
            (25, RETRI6),
            (24, RETRI7)
        ], RETRI

    )

    # CIIU
    ciiu = fields.Many2one('ciiu', CIIU)
    personType = fields.Selection(
        [
            (1, NATURAL),
            (2, COMPANY)
        ],
        PERSONTYPE,
        default=1
    )

    # Is Company: replace the field company_type
    company_type = fields.Selection(
        [
            ('person', 'Individual'),
            ('company', 'Compañia')
        ]
    )

    is_company = fields.Boolean(string=None)

    @api.one
    @api.depends('x_pn_numeroDocumento')
    def _concat_nit(self):
        """
        Concatenating and formatting the NIT number in order to have it consistent everywhere where it is needed
        @return: void
        """
        if self.x_pn_numeroDocumento is False:
            self.x_pn_numeroDocumento = ''

        self.formatedNit = ''

        # Formatting the NIT: xx.xxx.xxx-x
        s = str(self.x_pn_numeroDocumento)[::-1]
        newnit = '.'.join(s[i:i+3] for i in range(0, len(s), 3))
        newnit = newnit[::-1]

        nitList = [
            newnit,
            # Calling the NIT Function which creates the Verification Code:
            self._check_dv(str(self.x_pn_numeroDocumento))
        ]

        formatedNitList = []

        for item in nitList:
            # TODO Check if 0 creates problems with NIT that have a 0 in DV
            if item is not '' and item is not '0':
                formatedNitList.append(item)
                self.formatedNit = '-' .join(formatedNitList)


    @api.one
    @api.depends('x_pn_nombre1', 'x_pn_nombre2', 'x_pn_apellido1', 'x_pn_apellido2', 'companyName')
    def _concat_name(self):
        """
        This function concatenates the four name fields in order to be able to search
        for the entire name. On the other hand the original name field should not be editable anymore
        as the other fields should fill it up.
        @return: void
        """

        if self.x_pn_nombre1 is False:
            self.x_pn_nombre1 = ''

        if self.x_pn_nombre2 is False:
            self.x_pn_nombre2 = ''

        if self.x_pn_apellido1 is False:
            self.x_pn_apellido1 = ''

        if self.x_pn_apellido2 is False:
            self.x_pn_apellido2 = ''

        nameList = [
            self.x_pn_nombre1.encode(encoding='utf-8').strip(),
            self.x_pn_nombre2.encode(encoding='utf-8').strip(),
            self.x_pn_apellido1.encode(encoding='utf-8').strip(),
            self.x_pn_apellido2.encode(encoding='utf-8').strip()
        ]

        self.name = ''

        formatedList = []
        if self.companyName is False:
            for item in nameList:
                if item is not '':
                    formatedList.append(item)
            self.name = ' ' .join(formatedList)
        else:
            self.name = self.companyName

    @api.onchange('personType')
    def onChangePersonType(self):
        """
        Delete entries in fields once the type of person changes
        @return: void
        """
        if self.personType is 2:
            self.x_pn_nombre1 = ''
            self.x_pn_nombre2 = ''
            self.x_pn_apellido1 = ''
            self.x_pn_apellido2 = ''
        elif self.personType is 1:
            self.companyName = False

    @api.one
    @api.onchange('company_type')
    def onChangeCompanyType(self):
        if self.company_type == 'company':
            self.personType = 2
            self.is_company = True
        else:
            self.personType = 1
            self.is_company = False


    def _check_dv(self, nit):
        """
        Function to validate the check digit
        @param nit: Enter the NIT number without check digit
        @return: String
        """
        nitString = '0'*(15-len(nit)) + nit
        vl = list(nitString)
        result = (
                   int(vl[0])*71 +
                   int(vl[1])*67 +
                   int(vl[2])*59 +
                   int(vl[3])*53 +
                   int(vl[4])*47 +
                   int(vl[5])*43 +
                   int(vl[6])*41 +
                   int(vl[7])*37 +
                   int(vl[8])*29 +
                   int(vl[9])*23 +
                   int(vl[10])*19 +
                   int(vl[11])*17 +
                   int(vl[12])*13 +
                   int(vl[13])*7 +
                   int(vl[14])*3
               ) % 11

        if result in (0, 1):
            return str(result)
        else:
            return str(11-result)

    def _check_doc_number(self):
        # TODO check amount of digits in nit and co.
        return False