# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2016  Dominic Krimmer                                         #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Affero General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

# Partner Information App
from openerp import models, fields, api, exceptions
import re


class CountryStateCity(models.Model):
    """
    Model added to manipulate separately the cities on Partner address.
    """
    _description = 'Model to manipulate Cities'
    _name = 'res.country.state.city'

    code = fields.Char('City Code', size=5, help='Código DANE -5 dígitos-', required=True)
    name = fields.Char('City Name', size=64, required=True)
    state_id = fields.Many2one('res.country.state', 'State', required=True)
    country_id = fields.Many2one('res.country', 'Country', required=True)
    _order = 'code'


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
    DOCTYPE12 = "AS - Adulto sin identificación"
    DOCTYPE13 = "MS - Menor sin identificación"
    DOCTYPE14 = "NU - Número único de identificación"
    # TODO: Replace these names with the real terms and numbers
    DOCTYPE10 = "xx - DIAN"
    DOCTYPE11 = "xx - DIE"

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

    # Customer Location
    COUNTRY = 'País'
    DEPARTMENT = 'Departamento'
    MUNICIPALITY = 'Municipio'

    # --- Creating new fields --

    # Company Name
    companyName = fields.Char(COMPNAME)

    # companyType
    companyType = fields.Selection(related='company_type')

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
            (43, DOCTYPE8),
            (99, DOCTYPE10),
            (98, DOCTYPE11)

        ], DOCTYPE
    )
    x_pn_numeroDocumento = fields.Char(DOCNUM)
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

    # Replacing the field company_type
    company_type = fields.Selection(
        [
            ('person', 'Individual'),
            ('company', 'Compañia')
        ]
    )

    # Boolean if contact is a company or an individual
    is_company = fields.Boolean(string=None)

    # Verification digit
    dv = fields.Integer(string=None, store=True)

    # Country -> State -> Municipality - Logic
    xcountry = fields.Many2one('res.country', COUNTRY)
    xstate = fields.Many2one('res.country.state', DEPARTMENT)
    xcity = fields.Many2one('res.country.state.city', MUNICIPALITY)

    def onchange_location(self, cr, uid, ids, country_id=False, state_id=False):
        """
        This functions is a great helper when you enter the customers location.
        It solves the problem of various cities with the same name in a country
        @param country_id: Country Id (ISO)
        @param state_id: State Id (ISO)
        @return: object
        """
        if country_id:
            mymodel = 'res.country.state'
            filter_column = 'country_id'
            check_value = country_id
            domain = 'xstate'

        elif state_id:
            mymodel = 'res.country.state.city'
            filter_column = 'state_id'
            check_value = state_id
            domain = 'xcity'
        else:
            return {}

        obj = self.pool.get(mymodel)
        ids = obj.search(cr, uid, [(filter_column, '=', check_value)])
        return {'domain': {domain: [('id', 'in', ids)]}}


    @api.one
    @api.depends('x_pn_numeroDocumento')
    def _concat_nit(self):
        """
        Concatenating and formatting the NIT number in order to have it consistent everywhere where it is needed
        @return: void
        """
        # Executing only for Document Type 31 (NIT)
        if self.x_pn_tipoDocumento is 31:
            # First check if entered value is valid
            self._check_ident()
            self._check_ident_num()

            # Instead of showing "False" we put en empty string
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
                if item is not '':
                    formatedNitList.append(item)
                    self.formatedNit = '-' .join(formatedNitList)

            # Saving Verification digit in a proper field
            self.dv = nitList[1]


    @api.one
    @api.onchange('x_pn_nombre1', 'x_pn_nombre2', 'x_pn_apellido1', 'x_pn_apellido2', 'companyName')
    def _concat_name(self):
        """
        This function concatenates the four name fields in order to be able to search
        for the entire name. On the other hand the original name field should not be editable anymore
        as the other fields should fill it up.
        @return: void
        """
        # Avoiding that "False" will be written into the name field
        if self.x_pn_nombre1 is False:
            self.x_pn_nombre1 = ''

        if self.x_pn_nombre2 is False:
            self.x_pn_nombre2 = ''

        if self.x_pn_apellido1 is False:
            self.x_pn_apellido1 = ''

        if self.x_pn_apellido2 is False:
            self.x_pn_apellido2 = ''

        # Collecting all names in a field that will be concatenated
        nameList = [
            self.x_pn_nombre1.encode(encoding='utf-8').strip(),
            self.x_pn_nombre2.encode(encoding='utf-8').strip(),
            self.x_pn_apellido1.encode(encoding='utf-8').strip(),
            self.x_pn_apellido2.encode(encoding='utf-8').strip()
        ]

        formatedList = []
        if self.companyName is False:
            for item in nameList:
                if item is not '':
                    formatedList.append(item)
            self.name = ' ' .join(formatedList)
        else:
            self.name = self.companyName

    @api.one
    @api.onchange('name')
    def onChangeName(self):
        self._concat_name()

    @api.onchange('personType')
    def onChangePersonType(self):
        """
        Delete entries in name fields once the type of person changes to "company"
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
    @api.onchange('x_pn_tipoDocumento')
    def onChangeDocumentType(self):
        """
        If Document Type changes we delete the document number as for different document types there are different
        formats e.g. "Tarjeta de extranjeria" (21) allows letters in the value
        @return: void
        """
        self.x_pn_numeroDocumento = False

    @api.one
    @api.onchange('company_type')
    def onChangeCompanyType(self):
        """
        This function changes the person type field if the company type changes.
        If it is a company, document type 31 will be selected automatically as in colombia it's more probably that
        it will be choosen by the user.
        @return: void
        """
        if self.company_type == 'company':
            self.personType = 2
            self.is_company = True
            self.x_pn_tipoDocumento = 31
        else:
            self.personType = 1
            self.is_company = False
            self.x_pn_tipoDocumento = False

    @api.one
    @api.onchange('is_company')
    def onChangeIsCompany(self):
        """
        This function changes the person type field and the company type if checked / unchecked
        @return: void
        """
        if self.is_company is True:
            self.personType = 2
            self.company_type = 'company'
        else:
            self.is_company = False
            self.company_type = 'person'

    def _check_dv(self, nit):
        """
        Function to validate the check digit (DV). So there is no need to type it manually.
        @param nit: Enter the NIT number without check digit
        @return: String
        """
        if self.x_pn_tipoDocumento != 31:
            return str(nit)

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

    @api.constrains('x_pn_numeroDocumento')
    def _check_ident(self):
        """
        This function checks the number length in the Identification field. Min 6, Max 12 digits.
        @return: void
        """
        if len(str(self.x_pn_numeroDocumento)) < 2:
            raise exceptions.ValidationError("¡Error! Número de identificación debe tener entre 2 y 12 dígitos")
        elif len(str(self.x_pn_numeroDocumento)) > 12:
            raise exceptions.ValidationError("¡Error! Número de identificación debe tener entre 2 y 12 dígitos")

    @api.constrains('x_pn_numeroDocumento')
    def _check_ident_num(self):
        """
        This function checks the content of the identification fields: Type of document and number cannot be empty.
        There are two document types that permit letters in the identification field: 21 and 41
        The rest does not permit any letters
        @return: void
        """
        if self.x_pn_numeroDocumento != False and self.x_pn_tipoDocumento != 21 and self.x_pn_tipoDocumento != 41:
            if re.match("^[0-9]+$", self.x_pn_numeroDocumento) == None:
                    raise exceptions.ValidationError("¡Error! El número de identificación sólo permite números")

    @api.constrains('x_pn_tipoDocumento')
    def _checkDocType(self):
        """
        This function throws and error if there is no document type selected.
        @return: void
        """
        if self.x_pn_tipoDocumento is False:
            raise exceptions.ValidationError("¡Error! Porfavor escoga un tipo de identificación ")

    @api.constrains('x_pn_nombre1', 'x_pn_nombre2', 'companyName')
    def _check_names(self):
        """
        Double check: Although validation is checked within the frontend (xml) we check it again to get sure
        TODO: Check if obsolate :-)
        """
        if self.is_company is True:
            if self.companyName is False:
                raise exceptions.ValidationError("¡Error! Porfavor ingrese el nombre de la empresa")
        else:
            if self.x_pn_nombre1 is False or self.x_pn_nombre1 == '':
                raise exceptions.ValidationError("¡Error! Porfavor ingrese el nombre de la persona")



