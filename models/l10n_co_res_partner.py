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

    # Company Name
    companyName = fields.Char("Nombre de la compañia")

    # companyType
    companyType = fields.Selection(related='company_type')

    # Adding new name fields
    x_pn_nombre1 = fields.Char("Primer Nombre")
    x_pn_nombre2 = fields.Char("Segundo Nombre")
    x_pn_apellido1 = fields.Char("Primer Apellido")
    x_pn_apellido2 = fields.Char("Segundo Apellido")

    # Document information
    ''' TODO: Check these types and clarify: xx - DIAN, x - DIE '''
    doctype = fields.Selection(
        [
            (11, "11 - Registro civil de nacimiento"),
            (12, "12 - Tarjeta de identidad"),
            (13, "13 - Cédula de ciudadanía"),
            (21, "21 - Tarjeta de extranjería"),
            (22, "22 - Cédula de extranjería"),
            (31, "31 - NIT (Número de identificación tributaria)"),
            (41, "41 - Pasaporte"),
            (42, "42 - Documento de identificación extranjero"),
            (43, "43 - Sin identificación del exterior o para uso definido por la DIAN"),
            (99, "AS - Adulto sin identificación"),
            (98, "MS - Menor sin identificación"),
            (97, "NU - Número único de identificación"),

        ], "Tipo de identificación"
    )
    xidentification = fields.Char("Numero de Documento", store=True, help="Ingrese el numero de identificación")
    verificationDigit = fields.Integer('DV', size=2)
    formatedNit = fields.Char(
        string='NIT Formateado',
        compute="_concat_nit",
        store=True
    )

    # Tributate regime
    x_pn_retri = fields.Selection(
        [
            (6, "Simplificado"),
            (23, "P/Natural Común"),
            (7, "Común"),
            (11, "Gran Contribuyente  Auto-retenedor"),
            (22, "Internacional"),
            (25, "Común Auto-retenedor"),
            (24, "Gran Contribuyente")
        ], "Regímen Tributario"

    )

    # CIIU
    ciiu = fields.Many2one('ciiu', "Actividad CIIU")
    personType = fields.Selection(
        [
            (1, "natural"),
            (2, "juridica")
        ],
        "Tipo de persona",
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
    country_id = fields.Many2one('res.country', "País")
    state_id = fields.Many2one('res.country.state', "Departamento")
    city = fields.Many2one('res.country.state.city', "Municipio")

    # identification field has to be unique, therefore a constraint will validate it:
    _sql_constraints = [
        ('ident_unique',
         'UNIQUE(doctype,xidentification)',
         "¡Error! El número de identificación debe ser único!"),
    ]

    @api.one
    @api.depends('xidentification')
    def _concat_nit(self):
        """
        Concatenating and formatting the NIT number in order to have it consistent everywhere where it is needed
        @return: void
        """
        # Executing only for Document Type 31 (NIT)
        if self.doctype is 31:
            # First check if entered value is valid
            self._check_ident()
            self._check_ident_num()

            # Instead of showing "False" we put en empty string
            if self.xidentification is False:
                self.xidentification = ''

            self.formatedNit = ''

            # Formatting the NIT: xx.xxx.xxx-x
            s = str(self.xidentification)[::-1]
            newnit = '.'.join(s[i:i+3] for i in range(0, len(s), 3))
            newnit = newnit[::-1]

            nitList = [
                newnit,
                # Calling the NIT Function which creates the Verification Code:
                self._check_dv(str(self.xidentification))
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
    @api.onchange('doctype')
    def onChangeDocumentType(self):
        """
        If Document Type changes we delete the document number as for different document types there are different
        formats e.g. "Tarjeta de extranjeria" (21) allows letters in the value
        @return: void
        """
        self.xidentification = False

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
            self.doctype = 31
        else:
            self.personType = 1
            self.is_company = False
            self.doctype = False

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
        if self.doctype != 31:
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
            domain = 'state_id'

        elif state_id:
            mymodel = 'res.country.state.city'
            filter_column = 'state_id'
            check_value = state_id
            domain = 'city'
        else:
            return {}

        obj = self.pool.get(mymodel)
        ids = obj.search(cr, uid, [(filter_column, '=', check_value)])
        # return {'value': {'xcountry': country_id}}
        return {
            'domain': {domain: [('id', 'in', ids)]},
            'value': {domain: ''}
            }

    @api.constrains('xidentification')
    def _check_ident(self):
        """
        This function checks the number length in the Identification field. Min 6, Max 12 digits.
        @return: void
        """
        if len(str(self.xidentification)) < 2:
            raise exceptions.ValidationError("¡Error! Número de identificación debe tener entre 2 y 12 dígitos")
        elif len(str(self.xidentification)) > 12:
            raise exceptions.ValidationError("¡Error! Número de identificación debe tener entre 2 y 12 dígitos")

    @api.constrains('xidentification')
    def _check_ident_num(self):
        """
        This function checks the content of the identification fields: Type of document and number cannot be empty.
        There are two document types that permit letters in the identification field: 21 and 41
        The rest does not permit any letters
        @return: void
        """
        if self.xidentification != False and self.doctype != 21 and self.doctype != 41:
            if re.match("^[0-9]+$", self.xidentification) == None:
                    raise exceptions.ValidationError("¡Error! El número de identificación sólo permite números")

    @api.constrains('doctype', 'xidentification')
    def _checkDocType(self):
        """
        This function throws and error if there is no document type selected.
        @return: void
        """
        if self.doctype is False:
            raise exceptions.ValidationError("¡Error! Porfavor escoga un tipo de identificación")
        elif self.xidentification is False \
                and self.doctype is not 43 \
                and self.doctype is not 99\
                and self.doctype is not 98:
            raise exceptions.ValidationError("¡Error! Número de identificación es obligatorio!")

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



