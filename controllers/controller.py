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

from odoo import http
from odoo.http import request

class controller(http.Controller):

    @http.route('/l10n_co_res_partner/get_partner_state_city',  methods=['POST'], type='json', auth="public", website=True)
    def get_partner_state_city(self, **kw):
        _response = {}
        partner_id = kw.get('partner_id')
        query = "select xcity from res_partner where id = " + str(partner_id)
        request.cr.execute(query)
        partner_city = request.cr.dictfetchone()
        _response['xcity_id_'] = partner_city
        return _response

    @http.route('/l10n_co_res_partner/get_state_city',  methods=['POST'], type='json', auth="public", website=True)
    def get_state_city(self, **kw):
        _response = {'state_cities':None}
        state_id_ = kw.get('state_id')
        if(state_id_):
            query = "select code, id, name  from res_country_state_city where state_id = '" + str(state_id_) + "'"
            request.cr.execute(query)
            res_country_state_city = request.cr.dictfetchall()
            _response['state_cities'] = res_country_state_city
        return _response