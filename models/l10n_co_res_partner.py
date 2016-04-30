# -*- coding: utf-8 -*-

# Partner Information App
from openerp import models, fields, api


# Extend the Partner Model with some more fields


class PartnerInfoExtended(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # Declare some strings
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

    # Define the new fields
    name = fields.Char(
        string="Nombre completo",
        store=True,
        compute="_concat_name"
    )

    x_pn_nombre1 = fields.Char(PRIMARY_FNAME)
    x_pn_nombre2 = fields.Char(SECONDARY_FNAME)
    x_pn_apellido1 = fields.Char(PRIMARY_NAME)
    x_pn_apellido2 = fields.Char(SECONDARY_NAME)
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
    ciiu = fields.Many2one('ciiu', 'Actividad CIIU')
    personType = fields.Selection(
        [
            (1, 'natural'),
            (2, 'juridica')
        ], 'Tipo de persona'
    )

    companyName = fields.Char('Nombre de la compañia')


    @api.one
    @api.depends('x_pn_nombre1', 'x_pn_nombre2', 'x_pn_apellido1', 'x_pn_apellido2', 'companyName')
    def _concat_name(self):
        """
        This function concatinates the four name fields in order to be able to search
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
        for item in nameList:
            if item is not '':
                formatedList.append(item)
        self.name = ' ' .join(formatedList)
