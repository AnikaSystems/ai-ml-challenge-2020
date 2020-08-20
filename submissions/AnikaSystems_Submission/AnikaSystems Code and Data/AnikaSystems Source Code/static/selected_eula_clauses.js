/* Selected_Eulas.js - Render table that the classifier has detected. */

let VSELECTED_DOC = null; /* Reference to selected document in clauses table. */

$(document).ready(function () {
    console.log("Processing table init.");
    $('#Selected-Eulas').footable()
    init_download_doc();
    //renderClausesTable(VEULA_SAMPLE)
});


function renderClausesTable(my_data){
    /* Render all the clauses of a particular EULA by passing in the EULA struct. */ 
    VSELECTED_DOC = my_data;

    /* Hide the empty table indicator. */
    $("#table-empty-clauses").hide();
    //$("#table-empty-clauses").fadeOut("slow");

    /* Scroll to clauses. */
    $("body,html").animate({ scrollTop: $("#selected-clauses-ibox").offset().top }, 800);

    /* Set filename. */
    /* Create filename HTML. */
    let vfname_html = "";
    let vext = my_data["fname"].split(".").pop().toUpperCase();            
    if(vext == "PDF") {
        vfname_html = `<p><i style="color:red;" class="fa fa-file-pdf-o"></i>&nbsp;&nbsp;
                            <a data-toggle="tooltip" data-placement="right" 
                               title="Download file"
                               href="#">${my_data["fname"]}</a>
                        </p>`;

    } else if(vext == "DOCX") {
        vfname_html = `<p><i style="color:blue;" class="fa fa-file-word-o"></i>&nbsp;&nbsp;
                            <a data-toggle="tooltip" data-placement="right" 
                               title="Download file"
                               href="#">${my_data["fname"]}</a>
                        </p>`;
    }
    $("#clauses-fname").html(vfname_html);
    
    console.log("Rendering all clauses")
    let count = 0
    let htmlTable = ""

    /* Render each clause... */
    my_data["clauses"].forEach(clause => {
        count++
        htmlTable += `
            <tr data="${count}" onclick="showClause(this)" class="animated fadeIn">
                <td align="center" id="${count}-clause-txt" 
                    style="max-width:200px; overflow:hidden; text-overflow: ellipsis; white-space:nowrap;">
                   <a href="javascript:void(0)">${clause.text}</a>
                </td>

                <td align="center" id="${count}-clause-index" data-sort-value=${count}>${count}</td>
                
                <td align="center"><span id="${count}-clause-passed" class="badge badge-success">#</span></td>
                <td align="center" id="${count}-clause-confidence"><span style="font-size:12px;" class="##">${parseInt(clause.confidence*100)}%</span></td>
                <td align="center" id= "${count}-clause-page">${clause.text.length}</td>
            </tr>`

        /* Render clause as acceptable or unacceptable. */
        if (clause.acceptable){
            htmlTable = htmlTable.replace(`class="badge badge-success">#`, `class="badge badge-primary">True`);
        }
        else{
            htmlTable = htmlTable.replace(`class="badge badge-success">#`, `class="badge badge-danger">False`);
        }

        /* Render confidence badge. */
        if((parseInt(clause.confidence*100)) >= 80){
            htmlTable = htmlTable.replace('class="##">','class="badge bg-primary">')
        }
        else if((parseInt(clause.confidence*100)) >= 50 && (parseInt(clause.confidence*100)) < 80){
            htmlTable = htmlTable.replace('class="##">','class="badge bg-warning">')
        }
        else if((parseInt(clause.confidence*100)) < 50){
            htmlTable = htmlTable.replace('class="##">','class="badge bg-danger">')
        }
    });

    /* Render final output. */
    $("#Selected-Eulas-body").html(htmlTable);
    $('.footable').trigger('footable_redraw');
}


function showClause(identifier){
    /* Render the clause text in the clause text viewer, along with metadata. */
    
    /* Remove empty viewer indicators. */
    $("#viewer-empty-1").hide();
    $("#viewer-empty-2").hide();

    let cId = identifier.getAttribute('data');
    let cTxt = document.getElementById(cId + '-clause-txt').innerText;
    let cConfidence = document.getElementById(cId + '-clause-confidence').innerText;
    let cIndex = document.getElementById(cId + '-clause-index').innerText;
    let cPage = document.getElementById(cId + '-clause-page').innerText;
    let cPassed = document.getElementById(cId + '-clause-passed').innerText;

    let paragraphed = cTxt.replace(/(?<=[\w\s\,\d]+(\.|\?|\!)[\w\s\,\d]+(\.|\?|\!)[\w\s\,\d]+(\.|\?|\!)[\w\s\,\d]+(\.|\?|\!))\s/g, '<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');

    let html=`
        <span style="font-size:12px;" class="badge">Index: ${cIndex}</span>
        <span style="font-size:12px;" class="badge ##"></span>
        <span style="font-size:12px;" class="badge bg-primary">Confidence: ${cConfidence}</span>
        <br/><br/>
        <div style="height: 350px;">
            <div clas=" animated fadeInDown" style="border:1px solid #ebebeb; overflow: auto; padding:10px; height: 100%;">
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${paragraphed}
            </div>
        </div>
    `
    if(cPassed == "True"){
        html = html.replace(`badge ##">`,`badge badge-primary">Acceptable`);
        html = html.replace(`badge bg-primary">Confidence:`,`badge bg-primary">Confidence:`);
    }
    else{
        html = html.replace(`badge ##">`,`badge badge-danger">Unacceptable`);
        html = html.replace(`badge bg-primary">Confidence:`,`badge bg-warning">Confidence:`);
    }

    if((parseInt(cConfidence)) >= 80){
        html = html.replace(`badge bg-primary">Confidence:`,`badge bg-primary">Confidence:`);
    }
    else if((parseInt(cConfidence)) >= 50 && (parseInt(cConfidence)) < 80){
        html = html.replace(`badge bg-primary">Confidence:`,`badge bg-warning">Confidence:`);
    }
    else if((parseInt(cConfidence)) < 50){
        html = html.replace(`badge bg-primary">Confidence:`,`badge bg-danger">Confidence:`);
    }
    document.getElementById("clause-viewer").innerHTML = html;
}


function base64ToArrayBuffer(base64) {
    var binaryString = window.atob(base64);
    var binaryLen = binaryString.length;
    var bytes = new Uint8Array(binaryLen);
    for (var i = 0; i < binaryLen; i++) {
       var ascii = binaryString.charCodeAt(i);
       bytes[i] = ascii;
    }
    return bytes;
}


function init_download_doc() {
    $("#clauses-fname").click(function(e) {
        e.preventDefault();

        let vdoc = VSELECTED_DOC;
        
        let vdoc_id = vdoc["_id"]["$oid"];

        console.log("Download document: ", vdoc_id);
        toastr.success(`Downloading document ${vdoc['fname']}...`)

        $.get("/eula_bin?id="+vdoc_id, function(vresp) {
            vresp = JSON.parse(vresp);
            let vbyte_array = base64ToArrayBuffer(vresp["bytes"]["$binary"]);
            var blob = new Blob([vbyte_array], {type: "application/pdf"});
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            var fileName = vdoc["fname"];
            link.download = fileName;
            link.click();
            $("#dl-spinner").hide();
            return;
        });
    });
}