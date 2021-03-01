
/**
    This file is part of LibreOsteo.

    LibreOsteo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    LibreOsteo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with LibreOsteo.  If not, see <http://www.gnu.org/licenses/>.
*/
var rebuildindex = angular.module('loRebuildIndex', ['ngResource']);

rebuildindex.controller('RebuildIndexCtrl', ['$scope','$http', function($scope, $http)
{
    $scope.failed=false;
    $scope.finished=false;
    $scope.rebuildindex = function() {
      $http( {
                method: 'GET',
                url : 'internal/rebuild_index'
            }).then( function success(response)
            {
                $scope.finished = true;
            }, function error(response) {
                scope.failed = true
            });
    };
}]);
