/* previously_uploaded_eulas.js - Render documents that are stored in the database. */ 

$(document).ready(function() {
    console.log("Previously uploaded table init.");
    $('#previously-uploaded').footable();

    /* Retrieve db data every 3 seconds. */
    get_db_data();
    setInterval(function() {
        get_db_data();
    }, 12000);

    /* Install data exporters. */
    install_data_export();
});


function install_data_export() {
    /* Export table data as CSV or JSON files. */

    /* CSV */
    $("#export-csv-uploaded").click(function(e) {
        e.preventDefault();

        /* Create CSV string from table elements. */
        let vcsv = "File Name,Uploaded Date,# of Clauses,# Unacceptable,Overall Confidence Score";
        let vindex = 1;
        for(let vkey in VEULAS) {
            let vitem = VEULAS[vkey];
            vcsv += `\n"${vitem["fname"]}","${formatDate(vitem["upload_time"])}",${vitem["num_clauses"].length},${vitem["num_unacceptable"]},${vitem["avg_confidence"]}`;
            vindex++;
        }

        /* Create link and download. */
        let vfname = "Previously Uploaded EULAs.csv"

        $("<a />", {
            "download": vfname,
            "href" : "data:text/csv," + encodeURIComponent(vcsv)
            }).appendTo("body")
            .click(function() { $(this).remove() })[0].click();

        /* Create link and download. */
        toastr.success("Success! Table has been exported.");
    });


    /* JSON */
    $("#export-json-uploaded").click(function(e) {
        e.preventDefault();

        /* Create JSON struct from table elements. */
        let vjson = [];
        for(vitem in VEULAS) {
            vitem = VEULAS[vitem];
            vjson.push({
                "File Name": vitem["fname"],
                "Uploaded Date": formatDate(vitem["upload_time"]),
                "# of Clauses": vitem["num_clauses"].length,
                "# Unacceptable": vitem["num_unacceptable"],
                "Overall Confidence Score": vitem["avg_confidence"]
            })
        }

        /* Convert into exportable string. */
        let vjson_string = JSON.stringify(vjson, null, 4);

        /* Create link and download. */
        let vfname = "Previously Uploaded EULAs.json"

        $("<a />", {
            "download": vfname,
            "href" : "data:application/json," + encodeURIComponent(vjson_string)
            }).appendTo("body")
            .click(function() { $(this).remove() })[0].click();

        toastr.success("Success! Table has been exported.");
    });
}


function get_db_data() {
    /* Retrieve data from the database and render it to the table. */
    $.get("/eulas_db", function(vresp) {
        let vsize = vresp.length;
        console.log("[*] DB size: ", ((vsize / 1024)/1024) + "MB");
        vresp = JSON.parse(vresp);
        //console.log("[*] Eulas DB response: ", vresp);

        /* Re-init global EULAS struct for fast lookup. */
        VEULAS = {};

        let vqueue_html = "";

        for(let vitem of vresp) {
            /* Add to global EULAS struct. */
            VEULAS[vitem["_id"]["$oid"]] = vitem;

            /* Create upload time string */
            let vtime = vitem["upload_time"];//.split(".")[0];
            vtime = formatDate(vtime);

            /* Create confidence score HTML. */
            let vavg_accuracy = vitem["avg_confidence"]*100
            let vavg_label = "";
            if(vavg_accuracy > 79) vavg_label = "text-success";
            else if(vavg_accuracy > 59) vavg_label = "text-warning";
            else vavg_label = "text-danger";

            /* Create filename HTML. */
            let vfname_html = "";
            let vext = vitem["fname"].split(".").pop().toUpperCase();            
            if(vext == "PDF") {
                vfname_html = `<p><i style="color:red;" class="fa fa-file-pdf-o"></i>&nbsp;&nbsp;<a href="#">${vitem["fname"]}</a></p>`;

            } else if(vext == "DOCX") {
                vfname_html = `<p><i style="color:blue;" class="fa fa-file-word-o"></i>&nbsp;&nbsp;<a href="#">${vitem["fname"]}</a></p>`;
            }

            /* Assemble row HTML. */
            vqueue_html += `
                <tr class="eula_doc_link" doc_id="${vitem["_id"]["$oid"]}">
                <td><a href='#'>${vfname_html}</a></td>
                <td>${vtime}</td>
                <td class="center">${vitem["num_clauses"]}</td>
                <td class="center text-danger">${vitem["num_unacceptable"]}</td>
                <td class="center ${vavg_label}">${vavg_accuracy + "%"}</td>
                </tr>
                `;
        }

        $('#previously-uploaded-body').html(vqueue_html);
        
        if(vresp.length == 0) {
            $("#table-empty-previously-uploaded").show();
        } 
        else {
            $("#table-empty-previously-uploaded").hide();
        }

        $("#previously-uploaded").trigger('footable_redraw');
        //$('.footable').trigger('footable_redraw');

        init_eula_clicks();
    });
}


function init_eula_clicks() {
    /* Initialize all click handlers for the links in the Previously Uploaded DB's table. */
    $(".eula_doc_link").click(function(e) {
        e.preventDefault();
        let vdoc_id = $(this).closest("tr").attr("doc_id");
        console.log("[*] Selected DOC ID: ", vdoc_id);

        /* Fetch clauses data! */
        $.get("/eula?id="+vdoc_id, function(vresp) {
            vresp = JSON.parse(vresp);
            console.log("[*] Get EULA returned!", vresp);

            /* Render clauses! */
            renderClausesTable(vresp);

            /* Render full text... */
            VSELECTED_EULA_FULL_TEXT = vresp["eula_text"];
            console.log("EULA FULL TEXT: ", vresp);
            $("#eula-viewer").html(VSELECTED_EULA_FULL_TEXT.replace(/\n\n/g, "<br/><br/>"));
            //$("#eula-viewer").html(str_to_html_paragraphs(VSELECTED_EULA_FULL_TEXT));
        });

    });
}


/** Utils  ********************************************************************/

function str_to_html_paragraphs(vstr) {
    /* Turn a string into formatted paragraphs that can be rendered into HTML. */
    
    let vres = ""; /* Final result. */

    /* Split into sentences. */
    let vsentences = vstr.replace(/([.?!])\s*(?=[A-Z])/g, "$1|").split("|");

    let vindent = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";

    /* Init result with first indented sentence. */
    vres += `${vindent}${vsentences[0]}`;

    /* Join lines, adding indents... */
    for(let i = 1; i < vsentences.length; i++) {
        vres += ` ${vsentences[i]}`;
        if(i % 4 == 0) vres += `<br/><br/>${vindent}`;
    }

    return vres;
}


function average_accuracy(vclauses) {
    /* Determine average accuracy among array of clauses. */
    let res = 0;
    for(let vc of vclauses) {
        res += vc["confidence"];
    }
    res = res / vclauses.length;
    res = Math.round(res * 100)
    return res;
}


function num_unacceptable(vclauses) {
    /* Return number of unacceptable clauses in clauses array. */
    let res = 0;
    for(let vc of vclauses) {
        if(!vc["acceptable"]) ++res;
    }
    return res;
}

function formatDate(date) {
    var d = new Date(date);
    var hh = d.getHours();
    var m = d.getMinutes();
    var s = d.getSeconds();
    var dd = "AM";
    var h = hh;
    if (h >= 12) {
      h = hh - 12;
      dd = "PM";
    }
    if (h == 0) {
      h = 12;
    }
    m = m < 10 ? "0" + m : m;
  
    s = s < 10 ? "0" + s : s;
  
    /* if you want 2 digit hours:
    h = h<10?"0"+h:h; */
  
    var pattern = new RegExp("0?" + hh + ":" + m + ":" + s);
  
    var replacement = h + ":" + m;
    /* if you want to add seconds
    replacement += ":"+s;  */
    replacement += " " + dd;

    let vd = d.toISOString().split("T")[0].split("-");
    let vdate = vd[1] + "-" + vd[2] + "-" + vd[0];
  
    return `${vdate} @ ${replacement}`;
}