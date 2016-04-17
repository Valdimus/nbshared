define(['jquery', 'base/js/namespace', 'base/js/dialog', 'base/js/utils'], function ($, Jupyter, dialog, utils) {

  var ShareThisNb  = {
      help: 'Share this notebook',
      icon : 'fa-send',
      help_index : '',
      handler : function (env) {
          var on_success = undefined;
          var on_error = undefined;

          var p = $('<p/>').text("Please enter the name with the notebook will be shared.");
          var input = $('<input value="'+Jupyter.notebook.notebook_name+'"/>');
          console.log(input);
          var div = $('<div/>');

          div.append(p)
             .append(input);

          // get the canvas for user feedback
          var container = $('#notebook-container');

          function on_ok(){
              var filename = input.val();
              var url = utils.get_body_data("baseUrl") + 'shared/submit?notebook_id=' + encodeURIComponent(Jupyter.notebook.notebook_path);
              if(filename != "")
              {
                var suffix = ".ipynb";
                url+="&name="+encodeURIComponent(filename);
                if(filename.indexOf(suffix, filename.length - suffix.length) === -1){
                  url+=suffix;
                }
              }
              else {
                url+="&name="+encodeURIComponent(Jupyter.notebook.notebook_name);
              }
              //Fix, if the url finish by a .ipynb tornado don't want to serve it. So just add crap to the end for avoid it...
              url+="&fixtornado=wtf"

              var settings = {
                  url : url,
                  type : "GET",
                  success: function(data) {
                    // display feedback to user
                    var container = $('#notebook-container');
                    var feedback = '<div class="commit-feedback alert alert-success alert-dismissible" role="alert"> \
                                      <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button> \
                                      Shared \
                                       \
                                    </div>';

                    // display feedback
                    $('.commit-feedback').remove();
                    container.prepend(feedback);
                  },
                  error: function(data, code) {
                    // display feedback to user
                    var feedback = '<div class="commit-feedback alert alert-danger alert-dismissible" role="alert"> \
                                      <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button> \
                                      <strong>Warning!</strong> Something went wrong. \
                                      <div>Impossible to submit this notebook, it exits or you don\'t have the permission to submit notebook</div> \
                                    </div>';

                    // display feedback
                    $('.commit-feedback').remove();
                    container.prepend(feedback);
                  }
                }
                // display preloader during commit and push
                var preloader = '<img class="commit-feedback" src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.8/ajax-loader.gif">';
                container.prepend(preloader);

                // commit and push
                $.ajax(settings);
              };

            dialog.modal({
                body: div ,
                title: 'Share this notebook',
                buttons: {'Share':
                            { class:'btn-primary btn-large',
                              click:on_ok
                            },
                          'Cancel':{}
                    },
                notebook:env.notebook,
                keyboard_manager: env.notebook.keyboard_manager,
            });
          }
  }

  function _on_load(){

      // log to console
      console.info('Loaded Jupyter extension: nbshared')

      // register new action
      var action_name = Jupyter.keyboard_manager.actions.register(ShareThisNb, 'ShareThisNb', 'jupyter-nbshared')

      // add button for new action
      Jupyter.toolbar.add_buttons_group(['jupyter-nbshared:ShareThisNb'])

  }

  return {load_ipython_extension: _on_load };
    /*
    function open_dialog(env) {
        console.log(env);
        var p = $('<p/>').text("Please enter the notebooks name");
        var input = $('<textarea rows="4" cols="72"></textarea>');
        var div = $('<div/>');

        div.append(p)
           .append(input);
        dialog.modal({
          body: div,
          title: "Share this notebook",
          buttons: {
            "Share": {
              class: 'btn-primary btn-large',
              click: submit_example
            },
            "Cancel": {}
          }
        })
    }

    function submit_example () {

        var url = utils.get_body_data("baseUrl") + 'shared/submit?notebook_id=' + Jupyter.notebook.notebook_path;
        var win = window.open(url, '_blank');
        win.focus();
    };

    function add_button () {
        if (!Jupyter.toolbar) {
            $([Jupyter.events]).on("app_initialized.NotebookApp", add_button);
            return;
        }

        if ($("#submit-shared-button").length === 0) {
            Jupyter.toolbar.add_buttons_group([{
              'label'   : 'Share this notebook',
              'icon'    : 'fa-send',
              'callback': open_dialog,
              'id'      : 'submit-shared-button'
            }]);
        }
    };

    return {
        load_ipython_extension : add_button,
    };

    Jupyter.toolbar.add_buttons_group([{
      'label'   : 'Share this notebook',
      'icon'    : 'fa-send',
      'callback': open_dialog,
      'id'      : 'submit-shared-button'
    }]);
    */
});
