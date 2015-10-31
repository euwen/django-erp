'use strict';

$.extend({

    ajaxRequest: function(action, method, data, selector, callback) {

        var self = this;

        $.ajax({
            url: action,
            type: (method || "GET").toUpperCase(),
            data: data || {},
            complete: function(xhr, status) {

                var content = $('<div/>').html(xhr.responseText);

                if (selector) {

                    content = content.find(selector);
                }

                content = content.html().replace(/\s+/g, " ").replace("  ", "");

                // Has content: handle it.
                if (content) {

                    if (callback) { 

                        callback(content);

                    } else {

                        $(selector).html(content);
                    }

                // No content: maybe is a redirect...Follow it.
                } else {

                    var new_location = xhr.getResponseHeader("Location");

                    if (new_location) {

                        self.makeAjaxRequest(
                            new_location, 
                            "GET", 
                            null, 
                            selector, 
                            callback
                        );
                    }
                }
            }
        });
    }
});
