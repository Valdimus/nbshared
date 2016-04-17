define(function(require) {
    var $ = require('jquery');
    var Jupyter = require('base/js/namespace');
    var Shared = require('./nbshared');

    var shared_html = $([
        '<div id="shared" class="tab-pane">',
        '  <div id="shared_toolbar" class="row list_toolbar">',
        '    <div class="col-sm-8 no-padding">',
        '      <span id="shared_list_info" class="toolbar_info">A shared collection of notebooks. To contribute a new notebook to the list, open it and click the <span class="fa fa-send" style="margin: 3px;"></span> button.</span>',
        '    </div>',
        '    <div class="col-sm-4 no-padding tree-buttons">',
        '      <span id="shared_buttons" class="pull-right toolbar_buttons">',
        '      <button id="refresh_shared_list" title="Refresh shared list" class="btn btn-default btn-xs"><i class="fa fa-refresh"></i></button>',
        '      </span>',
        '    </div>',
        '  </div>',
        '  <div class="panel-group">',
        '    <div class="panel panel-default">',
        '      <div class="panel-heading">',
        '        Shared notebooks',
        '      </div>',
        '      <div class="panel-body">',
        '        <div id="unreviewed_shared_list" class="list_container">',
        '          <div id="unreviewed_shared_list_placeholder" class="row list_placeholder">',
        '            <div> There are no unreviewed shared. </div>',
        '          </div>',
        '        </div>',
        '      </div>',
        '    </div>',
        '  </div>   ',
        '</div>',
    ].join('\n'));

   function load() {
        if (!Jupyter.notebook_list) return;
        var base_url = Jupyter.notebook_list.base_url;
        $('head').append(
            $('<link>')
            .attr('rel', 'stylesheet')
            .attr('type', 'text/css')
            .attr('href', base_url + 'nbextensions/nbshared/nbshared.css')
        );
        $(".tab-content").append(shared_html);
        $("#tabs").append(
            $('<li>')
            .append(
                $('<a>')
                .attr('href', '#shared')
                .attr('data-toggle', 'tab')
                .text('Shared Notebooks')
                .click(function (e) {
                    window.history.pushState(null, null, '#shared');
                })
            )
        );
        var shared_notebooks = new Shared.Shared(
            '#unreviewed_shared_list',
            {
                base_url: Jupyter.notebook_list.base_url,
                notebook_path: Jupyter.notebook_list.notebook_path,
            }
        );
        shared_notebooks.load_list();
    }
    return {
        load_ipython_extension: load
    };
});
