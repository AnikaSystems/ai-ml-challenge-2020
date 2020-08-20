/* tutorial.js - Run the bootstrap tour that walks the user on how to use the application, component by component. */

/* When a user visited the site, Tour starts automatically. When Tour is finished, a cookie is placed in the browser of the visitor so that Tour will not start when the user reloads the page
*/

$(document).ready(function (){


    // Instance the tour
    var tour = new Tour({
        framework: "bootstrap4",
        container: ".wrapper-content",
        smartPlacement: true,
        backdrop: true,

        onEnd: function (tour) {
            $('html, body').animate({
                scrollTop: 0
            }, 500);

            Cookies.set("tutorial-completed", true);
            toastr.success("Congratulations! You may now check EULA's for unacceptable clauses.")
        },

        steps: [{
                element: ".navbar-static-top",
                title: "Welcome to EUL-AI!",
                content: "EUL-AI is an application designed to parse software license agreements and check wether each clause is acceptable or not to the GSA.",
                placement: "bottom"
            },
            {

                element: "#upload_eulas",
                title: "Start Uploading",
                content: "Your process starts here. Click 'Select Eulas' to choose PDF or MS Word documents for clauses classification. Click 'Upload' to start the classification process.",
            },
            {
                element: "#currently_processing_eulas",
                title: "View Documents in Queue",
                content: "Here you can see the progress of the parsing and classifying of the documents you have uploaded.",
            },
            {
                element: "#previously_uploaded_eulas",
                title: "EULA's Database",
                placement: "left",
                content: "This table will display all the EULAs that you have uploaded and classified in the past. Click the name of the file to view its clauses in detail.",

                onShown: function() {
                    let vbackdrop_height = $(".tour-backdrop").height();
                    let vheight = $("#previously_uploaded_eulas").height();
                    let vclauses_height = $('#selected-clauses-ibox').height();

                    $(".tour-backdrop").height(vbackdrop_height + vheight+vclauses_height - 50);
                }
             },
             {
                element: "#selected-clauses-ibox",
                title: "Acceptable Clauses",
                placement: "right",
                content: "Here you can view all the clauses of the selected license agreement. You can see wether they are classified as acceptable or not, and how confident the classification is. Click the clause to view its full text in detail.",
              },
              
              {
                element: "#clauses-fname",
                title: "Download Original EULA",
                placement: "right",
                content: "Click the name of the file (when it appears) to download the original EULA document.",
              },

             {
                element: "#selected_clause_text",
                title: "Inspect Clause Text",
                placement: "right",
                content: "View the full text of a particular clause, in order to understand why it has been classified the way it was. You can also click 'EULA Full Text' to view the contents of the EULA which contains this clause, as a whole.",
             }
        ]});

        //tour.init();
        //tour.start();


        // Cookies.remove("tutorial-completed");

        let vcompleted = Cookies.get("tutorial-completed");
        console.log("[*] Tutorial completed? ", vcompleted);

        if(!vcompleted) {
            $('html, body').animate({
                scrollTop: 0
            }, 500);

            setTimeout(function() {
                tour.restart();
            }, 1000);
        }


        $('[data-toggle="tooltip"]').tooltip()
    });