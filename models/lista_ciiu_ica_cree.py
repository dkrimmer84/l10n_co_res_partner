# -*- coding: utf-8 -*-

from openerp import models, fields, api

# CIIU, ICA y CREE


class CiiuIcaCree(models.Model):
    _name = "lista.ciiu_ica_cree"
    _description = "Lista CIIU, ICA y CREE"

    codigo = fields.Char('Código', required=True)
    name = fields.Char('Descripción')
    parent = fields.Many2one('lista.ciiu_ica_cree', 'Padre')
    type = fields.Char('Tipo', size=20, required=True)
    codigo_name = fields.Char(string="Codigo y Descripción", store=True, compute="_concat_name")

    @api.one
    @api.depends('codigo', 'name')
    def _concat_name(self):
        if self.codigo is False or self.name is False:
            self.codigo_name = ''
        else:
            self.codigo_name = str(self.codigo) + ' - ' + str(self.name)
