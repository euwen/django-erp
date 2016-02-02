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

                    var dom = $('<div/>').html(xhr.responseText.replace(/\s+/g, " ").replace("  ", ""));
                    var new_location = xhr.getResponseHeader("Location");

                    if (selector) {

                        dom = dom.find(selector);
                    }

                    // If it is a redirect, follow it.
                    if (new_location) {

                        erp.ui.request(
                            new_location, 
                            "GET", 
                            null, 
                            selector, 
                            callback
                        );

                    // Has content: handle it.
                    } else if (dom) {

                        if (callback) { 

                            callback(dom.html(), xhr);

                        } else {

                            $(selector || "html").html(dom.html());
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
    }
}
