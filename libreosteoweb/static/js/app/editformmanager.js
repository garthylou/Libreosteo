
/**
    This file is part of Libreosteo.

    Libreosteo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Libreosteo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Libreosteo.  If not, see <http://www.gnu.org/licenses/>.
*/
var editFormManager = angular.module('loEditFormManager', []);


function Callback(name, callback) {
  this.name = name;
  this.callback = callback;
}

editFormManager.factory('loEditFormManager', function() {
  var forms = [];
  var actions = ['edit', 'cancel', 'save', 'delete'];
  var callback_form = [];
  var triggers_form = [];
  return {
    add: function(form, action_list, trigger) {
      if (forms.indexOf(form) === -1) {
        forms.push(form);
      }
      angular.forEach(action_list, function(action, key) {
        if (action && actions.indexOf(action.name) != -1) {
          var idx_form = forms.indexOf(form);
          var should_add = true;
          var callbacks = null;
          angular.forEach(callback_form, function(value, key) {
            if (value.id == idx_form) {
              should_add = false;
              callbacks = value.callbacks;
            }
          });
          if (should_add) {
            callback_form.push({
              id: forms.indexOf(form),
              callbacks: [action]
            });
          } else {
            callbacks.push(action);
          }
        }
      });
      var idx_form = forms.indexOf(form);
      if (trigger) 
        triggers_form[idx_form] = trigger;
    },
    isavailable: function() {
      this.available = this._visibleCtrl() != null;
      return this.available;
    },
    available: false,
    action_available: function(name_action) {
      return this.action_callback(name_action) != null && this.action_trigger(name_action);
    },
    action_callback: function(name_action) {
      var idx_form = forms.indexOf(this._visibleCtrl());
      var callbacks = null;
      var callback = null;
      angular.forEach(callback_form, function(value, key) {
        if (value.id == idx_form) {
          callbacks = value.callbacks;
        }
      });
      if (callbacks != null) {
        angular.forEach(callbacks, function(value, key) {
          if (value.name == name_action) {
            callback = value;
          }
        });
      }
      return callback;
    },
    action_trigger: function(name_action) {
      var idx_form = forms.indexOf(this._visibleCtrl());
      var triggers = null;
      var trigger = true;
      angular.forEach(triggers_form, function(value, key) {
        if (key == idx_form) {
          triggers = value;
        }
      });
      if (triggers != null) {
        angular.forEach(triggers, function(value, key) {
          if (key == name_action) {
            if (value != null)
              trigger = value;
          }
        });
      }
      return trigger;
    },
    call_action: function(name) {
      this.action_callback(name).callback();
    },
    _visibleCtrl: function() {
      var visibleCtrl = null;
      angular.forEach(forms, function(value, key) {
        if (visibleCtrl != null && $(value).is(':visible')) {
          console.log("Cannot manage many ctrl....");
        }
        if (visibleCtrl == null && $(value).is(':visible')) {
          visibleCtrl = value;
        }
      });
      return visibleCtrl;
    }
  };
});

editFormManager.directive('editFormControl', ['$timeout', function($timeout) {
  return {
    restrict: 'A',
    scope: {
      save: "=save",
      trigger: "=trigger",
      edit: "=edit",
      cancel: "=cancel",
      delete: "=delete",
      saveOnLostFocus: "=saveOnLostFocus"
    },
    compile: function(element, attr) {
      if (!attr.save) {
        attr.save = null;
      }
      if (!attr.edit) {
        attr.edit = null;
      }
      if (!attr.cancel) {
        attr.cancel = null;
      }
      if (!attr.delete) {
        attr.delete = null;
      }
      if(!attr.saveOnLostFocus){
        attr.saveOnLostFocus = false;
      }
    },
    controller: ['$scope', '$routeParams', 'loEditFormManager', '$element', function($scope, $routeParams, loEditFormManager, $element) {
      var actions = [];
      if ($scope.save != null) {
        actions.push(new Callback('save', $scope.save));
      }
      if ($scope.edit != null) {
        actions.push(new Callback('edit', $scope.edit));
      }
      if ($scope.cancel != null) {
        actions.push(new Callback('cancel', $scope.cancel));
      }
      if ($scope.delete != null) {
        actions.push(new Callback('delete', $scope.delete));
      }
      $timeout(function() {
        loEditFormManager.add($element, actions, $scope.trigger);
      });

      /**
       * Handle a user attempt to leave a view containing unsaved data
       *
       * May autosave, or prompt user, or let leave.
       *
       * @param {event} event - The event of leaving the view (cancel-able)
       * @param{boolean} askUser - Wether we ask if he really wants to leave
       */
      var quitConfirmationMsg = gettext(
        'There are unsaved changes. Do you really want to leave this page ?'
      );

      function handleUnsavedForm(event, askUser) {
        if ($element.hasClass('ng-dirty')) {
          if ($scope.saveOnLostFocus) {
            $scope.save();
            $scope.trigger.save = false;

          } else if (askUser) {
            var quitAnyway = confirm(quitConfirmationMsg);
            if (!quitAnyway) {
              event.preventDefault(); // prevent view change
            }
          }
        }
      }

      // tab change
      $scope.$on('uiTabChange', function(event) {
        // :visible is a hack to figure out if we are current tab.
        if ($element.is(':visible')) {
          handleUnsavedForm(event, false);
        }
      });
      // router view change
      $scope.$on('$locationChangeStart', function(event) {
        handleUnsavedForm(event, true);
      });

      // Window/tab quit or real link click
      //
      // beforeunload is an uncommon event:
      // - on most browsers, confirm() calls within its body will be ignored
      // - on some browsers, you can issue a custom message, but on others
      //   won't accept it (in favor of built-in message)
      // - it is hard to get sure an AJAX call is made (for autosave)
      // - API depend on browser
      //
      // https://developer.mozilla.org/en-US/docs/Web/Events/beforeunload
      //
      // So, best-effort: we ask for confirmation, optionaly with custom
      // message.
      function onQuit(event) {
        if ($element.hasClass('ng-dirty')) {
          event.returnValue = quitConfirmationMsg;
          return quitConfirmationMsg;
        }
      };
      window.addEventListener('beforeunload', onQuit);
      $scope.$on('$destroy', function() {
        window.removeEventListener('beforeunload', onQuit);
      });
    }],
  }
}]);



var getStackTrace = function() {
  var obj = {};
  Error.captureStackTrace(obj, getStackTrace);
  return obj.stack;
};
