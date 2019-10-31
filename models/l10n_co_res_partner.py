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

# Extended Partner Module
from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
import re
import logging
_logger = logging.getLogger(__name__)


class CountryStateCity(models.Model):
    """
    Model added to manipulate separately the cities on Partner address.
    """
    _description = 'Model to manipulate Cities'
    _name = 'res.country.state.city'
    _order = 'code'

    code = fields.Char('City Code', size=5, help='Code DANE - 5 digits-',
                       required=True)
    name = fields.Char('City Name', size=64, required=True)
    state_id = fields.Many2one('res.country.state', 'State', required=True)
    country_id = fields.Many2one('res.country', 'Country', required=True)


class PartnerInfoExtended(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # Company Name (legal name)
    companyName = fields.Char("Name of the Company")

    # Brand Name (e.j. Claro Móvil = Brand, COMCEL SA = legal name)
    companyBrandName = fields.Char("Brand")

    # companyType
    companyType = fields.Selection(related='company_type')

    # Adding new name fields
    x_name1 = fields.Char("First Name")
    x_name2 = fields.Char("Second Name")
    x_lastname1 = fields.Char("Last Name")
    x_lastname2 = fields.Char("Second Last Name")

    # Document information
    doctype = fields.Selection(
        [
            (1, "No identification"),
            (11, "11 - Birth Certificate"),
            (12, "12 - Identity Card"),
            (13, "13 - Citizenship Card"),
            (21, "21 - Alien Registration Card"),
            (22, "22 - Foreigner ID"),
            (31, "31 - TAX Number (NIT)"),
            (41, "41 - Passport"),
            (42, "42 - Foreign Identification Document"),
            (43, "43 - No Foreign Identification")

        ], "Type of Identification"
    )
    xidentification = fields.Char("Document Number", store=True,
                                  help="Enter the Identification Number")
    verificationDigit = fields.Integer('VD', size=2)
    formatedNit = fields.Char(
        string='NIT Formatted',
        compute="_compute_concat_nit",
        store=True
    )

    # Tributate regime
    x_pn_retri = fields.Selection(
        [
            (6, "Simplified"),
            (23, "Natural Person"),
            (7, "Common"),
            (11, "Great Taxpayer Autorretenedor"),
            (22, "International"),
            (25, "Common Autorretenedor"),
            (24, "Great Contributor")
        ], "Tax Regime"

    )

    # CIIU - Clasificación Internacional Industrial Uniforme
    ciiu = fields.Many2one('ciiu', "ISIC Activity")
    personType = fields.Selection(
        [
            (1, "Natural"),
            (2, "Juridical")
        ],
        "Type of Person",
        default=1
    )

    # Replacing the field company_type
    company_type = fields.Selection(
        [
            ('person', 'Individual'),
            ('company', 'Company')
        ]
    )

    # Boolean if contact is a company or an individual
    is_company = fields.Boolean(string=None)

    # Verification digit
    dv = fields.Integer(string=None, store=True)

    # Country -> State -> Municipality - Logic
    country_id = fields.Many2one('res.country', "Country")
    xcity = fields.Many2one('res.country.state.city', "Municipality")
    city = fields.Char(related="xcity.name")

    # identification field has to be unique,
    # therefore a constraint will validate it:
    _sql_constraints = [
        ('ident_unique',
         'UNIQUE(doctype,xidentification)',
         "Identification number must be unique!"),
    ]

    # Check to handle change of Country, City and Municipality
    change_country = fields.Boolean(string="Change Country / Department?",
                                    default=True, store=False)

    # Name of point of sales / delivery contact
    pos_name = fields.Char("Point of Sales Name")

    # Birthday of the contact (only useful for non-company contacts)
    xbirthday = fields.Date("Birthday")

    def get_doctype(self, cr, uid, context={'lang': 'es_CO'}):
        result = []
        for item in self.pool.get('res.partner').fields_get(cr, uid, allfields=['doctype'], context=context)['doctype']['selection']:
            result.append({'id': item[0], 'name': item[1]})
        return result

    def get_persontype(self, cr, uid, context={'lang': 'es_CO'}):
        result = []
        for item in self.pool.get('res.partner').fields_get(cr, uid, allfields=['personType'], context=context)['personType']['selection']:
            result.append({'id': item[0], 'name': item[1]})
        return result

    @api.depends('xidentification')
    def _compute_concat_nit(self):
        """
        Concatenating and formatting the NIT number in order to have it
        consistent everywhere where it is needed
        @return: void
        """
        # Executing only for Document Type 31 (NIT)
        for partner in self:
            if partner.doctype is 31:
                # First check if entered value is valid
                self._check_ident()
                self._check_ident_num()

                # Instead of showing "False" we put en empty string
                if partner.xidentification is False:
                    partner.xidentification = ''
                else:
                    partner.formatedNit = ''

                    # Formatting the NIT: xx.xxx.xxx-x
                    s = str(partner.xidentification)[::-1]
                    newnit = '.'.join(s[i:i+3] for i in range(0, len(s), 3))
                    newnit = newnit[::-1]

                    nitList = [
                        newnit,
                        # Calling the NIT Function
                        # which creates the Verification Code:
                        self._check_dv(str(partner.xidentification))
                    ]

                    formatedNitList = []

                    for item in nitList:
                        if item is not '':
                            formatedNitList.append(item)
                            partner.formatedNit = '-' .join(formatedNitList)

                    # Saving Verification digit in a proper field
                    for pnitem in self:
                        pnitem.dv = nitList[1]

    @api.onchange('x_name1', 'x_name2', 'x_lastname1', 'x_lastname2', 'companyName',
                  'pos_name', 'companyBrandName')
    def _concat_name(self):
        """
                This function concatenates the four name fields in order to be able to
                search for the entire name. On the other hand the original name field
                should not be editable anymore as the new name fields should fill it up
                automatically.
                @return: void
                """
        # Avoiding that "False" will be written into the name field
        if not self.x_name1:
            self.x_name1 = ''

        if not self.x_name2:
            self.x_name2 = ''

        if not self.x_lastname1:
            self.x_lastname1 = ''

        if not self.x_lastname2:
            self.x_lastname2 = ''

        # Collecting all names in a field that will be concatenated
        nameList = [
            self.x_name1.encode(encoding='utf-8').strip(),
            self.x_name2.encode(encoding='utf-8').strip(),
            self.x_lastname1.encode(encoding='utf-8').strip(),
            self.x_lastname2.encode(encoding='utf-8').strip()
        ]

        formatedList = []
        if self.companyName is False:
            if self.type == 'delivery':
                self.name = self.pos_name
                self.x_name1 = False
                self.x_name2 = False
                self.x_lastname1 = False
                self.x_lastname2 = False
                self.doctype = 1
            else:
                for item in nameList:
                    if item is not b'':
                        formatedList.append(item.decode('UTF-8'))
                    self.name = ' '.join(formatedList).title()
        else:
            # Some Companies are know for their Brand, which could conflict from the users point of view while
            # searching the company (e.j. o2 = brand, Telefonica = Company)
            if self.companyBrandName is not False:
                delimiter = ', '
                company_list = (self.companyBrandName, self.companyName)
                self.name = delimiter.join(company_list).title()
            else:
                self.name = self.companyName.title()

    @api.onchange('name')
    def on_change_name(self):
        """
        The name field gets concatenated by the four name fields.
        If a user enters a value anyway, the value will be deleted except first
        name has no value. Reason: In certain forms of odoo it is still
        possible to add value to the original name field. Therefore we have to
        ensure that this field can receive values unless we offer the four name
        fields.
        @return: void
        """
        if self.x_name1 is not False:
            if len(self.x_name1) > 0:
                self._concat_name()
        if self.companyName is not False:
            if len(self.companyName) > 0:
                self._concat_name()

    @api.onchange('personType')
    def on_change_person_type(self):
        """
        Delete entries in name and company fields once the type of person
        changes. This avoids unnecessary entries in the database and makes the
        contact cleaner and ready for analysis
        @return: void
        """
        if self.personType is 2:
            self.x_name1 = ''
            self.x_name2 = ''
            self.x_lastname1 = ''
            self.x_lastname2 = ''
            self.x_pn_retri = 7
        elif self.personType is 1:
            self.companyName = False
            self.companyBrandName = False
            self.x_pn_retri = False

    @api.onchange('doctype')
    def on_change_document_type(self):
        """
        If Document Type changes we delete the document number as for different
        document types there are different rules that apply e.g. foreign
        documents (e.g. 21) allows letters in the value. Here we reduce the
        risk of having corrupt information about the contact.
        @return: void
        """
        self.xidentification = False

    @api.onchange('company_type')
    def on_change_company_type(self):
        """
        This function changes the person type once the company type changes.
        If it is a company, document type 31 will be selected automatically as
        in Colombia it's more likely that it will be chosen by the user.
        @return: void
        """
        if self.company_type == 'company':
            self.personType = 2
            self.is_company = True
            self.doctype = 31
        else:
            self.personType = 1
            self.is_company = False
            self.doctype = 1

    @api.onchange('is_company')
    def on_change_is_company(self):
        """
        This function changes the person type field and the company type if
        checked / unchecked
        @return: void
        """
        if self.is_company is True:
            self.personType = 2
            self.company_type = 'company'
            self.xbirthday = False
        else:
            self.is_company = False
            self.company_type = 'person'

    @api.onchange('change_country')
    def on_change_address(self):
        """
        This function changes the person type field and the company type if
        checked / unchecked
        @return: void
        """
        if self.change_country is True:
            self.country_id = False
            self.state_id = False
            self.xcity = False

    def _check_dv(self, nit):
        """
        Function to calculate the check digit (DV) of the NIT. So there is no
        need to type it manually.
        @param nit: Enter the NIT number without check digit
        @return: String
        """
        for item in self:
            if item.doctype != 31:
                return str(nit)

            nitString = '0'*(15-len(nit)) + nit
            vl = list(nitString)
            result = (
                             int(vl[0])*71 + int(vl[1])*67 + int(vl[2])*59 + int(vl[3])*53 +
                             int(vl[4])*47 + int(vl[5])*43 + int(vl[6])*41 + int(vl[7])*37 +
                             int(vl[8])*29 + int(vl[9])*23 + int(vl[10])*19 + int(vl[11])*17 +
                             int(vl[12])*13 + int(vl[13])*7 + int(vl[14])*3
                     ) % 11

            if result in (0, 1):
                return str(result)
            else:
                return str(11-result)

    def onchange_location(self, cr, uid, ids, country_id=False,
                          state_id=False):
        """
        This functions is a great helper when you enter the customer's
        location. It solves the problem of various cities with the same name in
        a country
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
            domain = 'xcity'
        else:
            return {}

        obj = self.pool.get(mymodel)
        ids = obj.search(cr, uid, [(filter_column, '=', check_value)])
        return {
            'domain': {domain: [('id', 'in', ids)]},
            'value': {domain: ''}
        }

    @api.constrains('xidentification')
    def _check_ident(self):
        """
        This function checks the number length in the Identification field.
        Min 6, Max 12 digits.
        @return: void
        """
        for item in self:
            if item.doctype is not 1:
                msg = _('Error! Number of digits in Identification number must be'
                        'between 2 and 12')
                if len(str(item.xidentification)) < 2:
                    raise exceptions.ValidationError(msg)
                elif len(str(item.xidentification)) > 12:
                    raise exceptions.ValidationError(msg)

    @api.constrains('xidentification')
    def _check_ident_num(self):
        """
        This function checks the content of the identification fields: Type of
        document and number cannot be empty.
        There are two document types that permit letters in the identification
        field: 21 and 41. The rest does not permit any letters
        @return: void
        """
        for item in self:
            if item.doctype is not 1:
                if item.xidentification is not False and \
                        item.doctype != 21 and \
                        item.doctype != 41:
                    if re.match("^[0-9]+$", item.xidentification) is None:
                        msg = _('Error! Identification number can only '
                                'have numbers')
                        raise exceptions.ValidationError(msg)

    @api.constrains('doctype', 'xidentification')
    def _checkDocType(self):
        """
        This function throws and error if there is no document type selected.
        @return: void
        """
        if self.doctype is not 1:
            if self.doctype is False:
                msg = _('Error! Please choose an identification type')
                raise exceptions.ValidationError(msg)
            elif self.xidentification is False and self.doctype is not 43:
                msg = _('Error! Identification number is mandatory')
                raise exceptions.ValidationError(msg)

    @api.constrains('x_name1', 'x_name2', 'companyName')
    def _check_names(self):
        """
        Double check: Although validation is checked within the frontend (xml)
        we check it again to get sure
        """
        if self.is_company is True:
            if self.personType is 1:
                if self.x_name1 is False or self.x_name1 == '':
                    msg = _('Error! Please enter the persons name')
                    raise exceptions.ValidationError(msg)
            elif self.personType is 2:
                if self.companyName is False:
                    msg = _('Error! Please enter the companys name')
                    raise exceptions.ValidationError(msg)
        elif self.type == 'delivery':
            if self.pos_name is False or self.pos_name == '':
                msg = _('Error! Please enter the persons name')
                raise exceptions.ValidationError(msg)
        else:
            if self.x_name1 is False or self.x_name1 == '':
                msg = _('Error! Please enter the name of the person')
                raise exceptions.ValidationError(msg)

    @api.constrains('personType')
    def _check_person_type(self):
        """
        This function checks if the person type is not empty
        @return: void
        """
        if self.personType is False:
            msg = _('Error! Please select a person type')
            raise exceptions.ValidationError(msg)
