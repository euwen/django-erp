'use strict';

var erp = { 
    ui: {
        openModal: function(parent, content) {

            $(parent)
                .after(content)
                .siblings('.modal')
                .modal({
                    onHidden: function(e) { $(this).remove(); }
                })
                .modal('show');

            $.readyFn.execute();
        },

        request: function(action, method, data, selector, callback) {

            var self = $(this);

            $.ajax({
                url: action,
                type: (method || "GET").toUpperCase(),
                data: data || {},
                async: true,
                error: function(xhr) { console.log(xhr.responseText); },
                complete: function(xhr, status) {

                    // If it is a redirect to another URL, follow it.
                    if (xhr.status == 278) {

                        window.location.href = xhr.getResponseHeader("Location");

                    // Has content: handle it.
                    } else {
                        
                        var dom = $('<div/>').html(xhr.responseText.replace(/\s+/g, " ").replace("  ", ""));

                        if (dom) {

                            if (callback) { 

                                callback(dom.html(), xhr);

                            } else {

                                if (selector) {

                                    dom = dom.find(selector);
                                }

                                $(selector || "html").html(dom.html());

                                $.readyFn.execute();
                            }
                        }
                    }
                }
            });
        },

        requestLink: function(evt, selector, callback) {

            var self = $(evt.currentTarget);
            var action = self.attr("href");

            if (action && action != '/' && action != '#' && action != '/users/logout/' && action != '/users/login/') {

                evt.preventDefault();
                evt.stopPropagation();

                self.attr("disabled", true);

                erp.ui.request(action, "GET", {}, selector, callback);

                self.attr("disabled", false);
            }
        },

        requestLinkInModal: function(evt, callback) {

            erp.ui.requestLink(evt, null, callback || function(content, xhr, status) {

                erp.ui.openModal($(evt.currentTarget), content);
            });
        },

        handleFormSubmit: function(evt, callback) {

            evt.preventDefault();
            evt.stopPropagation();

            var submit_button = $(this);
            var form = submit_button.closest('form');
            var action = form.attr("action");
            var method = form.attr("method");
            var data = form.serialize();

            submit_button.attr("disabled", true);

            erp.ui.request(action, method, data, '.modal', callback);

            submit_button.attr("disabled", false);
        },
    }
}
