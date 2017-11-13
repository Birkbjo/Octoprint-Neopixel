/*
 * View model for OctoPrint-Neopixel-pwm
 *
 * Author: Birk Johansson
 * License: AGPLv3
 */
$(function() {
    function NeopixelViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        NeopixelViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ /* "loginStateViewModel", "settingsViewModel" */ ],

        // e.g. #settings_plugin_neopixel-pwm, #tab_plugin_neopixel-pwm, ...
        [ /* ... */ ]
    ]);
});
