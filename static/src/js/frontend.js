odoo.define('module.DianInvoice', function(require) {
    "use strict";
    var rpc = require('web.rpc');
    var loaded = false;
    $(document).ready(function() 
    {
        var flagLoaded = false;
        var mainIntervalTime = 2500;
        setInterval(function() 
        {
            if($("form.checkout_autoformat").length>0)
            {
                init_xcity_selection()             

                $(document).on("blur", "input[name='xidentification']", function() 
                {
                    update_nit_cod_verification();
                });
                $(document).on("blur", "input[name='x_name1']", function()
                {
                    update_customer_full_name();
                });
                $(document).on("blur", "input[name='x_name2']", function() 
                {
                    update_customer_full_name();
                });
                $(document).on("blur", "input[name='x_lastname1']", function() 
                {
                    update_customer_full_name();
                });
                $(document).on("blur", "input[name='x_lastname2']", function() 
                {
                    update_customer_full_name();
                }); 
                $(document).on("blur", "input[name='company_name']", function() 
                {
                    set_document_type();
                    $("input[name='companyBrandName']").val($(this).val());
                }); 
                $(document).on("change", "select[name='state_id']", function() 
                {
                    populate_xcity_field(false);
                });  
                $(document).on("change", "select[name='xcity']", function() 
                {
                    var xcity_zip = $(this).find('option:selected').attr('code');
                    $("input[name='zip']").val(xcity_zip);
                }); 

            }
        
        function init_xcity_selection() 
        {
            if($("select[name='xcity']").find('option').length == 0)
            {                
                populate_xcity_field(true);
            }
        }

        function update_nit_cod_verification()
        {
            var doc_type = $("select[name='doctype']").val()
            var doc_num  = $("input[name='xidentification']").val()
            if(parseInt(doc_type)==31)
            {
                var doc_num_code = dian_nit_codigo_verificacion(doc_num);
                $("input[name='verificationDigit']").val(doc_num_code);                
            }
            
        }
        function set_document_type()
        {
            var company_name = $("input[name='company_name']").val(); 
            if(String(company_name)=="")
            {
                $("select[name='doctype']").val(13);
            }
            if(String(company_name).length > 0 )
            {
                $("select[name='doctype']").val(31);
            }
        }
        function update_customer_full_name()
        {
            var first_name_1 = $("input[name='x_name1']").val();
            var first_name_2 = $("input[name='x_name2']").val();
            var last_name_1 = $("input[name='x_lastname1']").val();
            var last_name_2 = $("input[name='x_lastname2']").val();
            var full_name = String(first_name_1) + String(" ") + String(first_name_2) + String(" ") + String(last_name_1) + String(" ") + String(last_name_2);
            $("input[name='name']").val(full_name);
            $("input[name='pos_name']").val(full_name);
        }
        function populate_xcity_field(set_partner_city=false)
        {
            var state_id = $("select[name='state_id']").val();

            var data = { "params": { "state_id": state_id } }
            
                $.ajax({
                    type: "POST",
                    url: '/l10n_co_res_partner/get_state_city',
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: "application/json",
                    async: false,
                    success: function(response) 
                    {
                        if (response.result.state_cities) 
                        {

                            try {
                                    var xcities_options = String();

                                    var xcities = response.result.state_cities;
                                    
                                    xcities.forEach(function (xcitie, index) 
                                    {
                                        xcities_options = String(xcities_options) + "<option value='" + String(xcitie.id) + "' code='" + String(xcitie.code) + "'>" + String(xcitie.name) + "</option>";
                                        //console.log(xcities_options)
                                    });  
                                    
                                    $("select[name='xcity']").html('');
                                    $("select[name='xcity']").append(xcities_options);

                                    if(set_partner_city)
                                    {
                                        

                                        var partner_id = $("input[name='partner_id']").val();
                                        var data = { "params": { "partner_id": partner_id } }

                                        $.ajax
                                        ({
                                            type: "POST",
                                            url: '/l10n_co_res_partner/get_partner_state_city/',
                                            data: JSON.stringify(data),
                                            dataType: 'json',
                                            contentType: "application/json",
                                            async: false,
                                            success: function(response) 
                                            {
                                                if (response.result.xcity_id_!=null) 
                                                {
                                                    $("select[name='xcity']").val(response.result.xcity_id_.xcity) 
                                                }
                                            }
                                        });
                                    }

                                }
                            catch (error) 
                            {console.log(error) }
                        }
            
                    }
                });

        }

        function dian_nit_codigo_verificacion(myNit) 
        {
            var vpri,
                x,
                y,
                z;
        
            // Se limpia el Nit
            myNit = myNit.replace(/\s/g, ""); // Espacios
            myNit = myNit.replace(/,/g, ""); // Comas
            myNit = myNit.replace(/\./g, ""); // Puntos
            myNit = myNit.replace(/-/g, ""); // Guiones
        
            // Se valida el nit
            if (isNaN(myNit)) {
                console.log("El nit/cédula '" + myNit + "' no es válido(a).");
                return "";
            };
        
            // Procedimiento
            vpri = new Array(16);
            z = myNit.length;
        
            vpri[1] = 3;
            vpri[2] = 7;
            vpri[3] = 13;
            vpri[4] = 17;
            vpri[5] = 19;
            vpri[6] = 23;
            vpri[7] = 29;
            vpri[8] = 37;
            vpri[9] = 41;
            vpri[10] = 43;
            vpri[11] = 47;
            vpri[12] = 53;
            vpri[13] = 59;
            vpri[14] = 67;
            vpri[15] = 71;
        
            x = 0;
            y = 0;
            for (var i = 0; i < z; i++) {
                y = (myNit.substr(i, 1));
                // console.log ( y + "x" + vpri[z-i] + ":" ) ;
        
                x += (y * vpri[z - i]);
                // console.log ( x ) ;    
            }
        
            y = x % 11;
            // console.log ( y ) ;
        
            return (y > 1) ? 11 - y : y;
        }
        
        },mainIntervalTime);
    });
});
    