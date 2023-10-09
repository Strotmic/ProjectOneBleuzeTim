
"use strict"
const lanIP = `${window.location.hostname}:5000`;
const socketio = io(lanIP);

let htmlTiles, htmlNieuws, htmlTable, htmlReport;
let searchParams, cat_id;

"use strict"
const lanIP = `${window.location.hostname}:5000`;
const socketio = io(lanIP);

let htmlTiles, htmlNieuws, htmlTable, htmlReport;
let searchParams, cat_id;

const splitStr = function(string){
  return string.split('__',1)[0]
}

const showAllCat = function(jsonObject){
  console.info(jsonObject)
  let htmlString = ''
  for(let c of jsonObject.categories){
    htmlString += `<div class="js-tile c-tile c-tile--eenheidverbergen c-tile--${splitStr(c.class)}">
    <div class="c-tile__header">
      <img src="images/${c.image}.svg" alt="${c.image}">
      <span class="c-tile__info">
        <span class="c-tile__title">${c.naam} <span class="c-tile__eenheid">(${c.eenheid})</span></span>
        <span class="c-tile__subtitle">${c.ondertitel}</span>
      </span>
    </div>
    <a class="c-tile__link" href="detail.html?cat_id=${c.id}">
      <span>Bekijk data</span>
      <img src="images/pijltje.svg" alt="pijltje">
    </a>
  </div>`
  }
  htmlTiles.innerHTML = htmlString;
  showEenheid()
}

const showEenheid = function(){
  const tile = document.querySelectorAll('.js-tile')
  for(let t of tile){
    t.addEventListener('mouseenter', function(){
      t.classList.remove('c-tile--eenheidverbergen')
    })
    t.addEventListener('mouseleave', function(){
      t.classList.add ('c-tile--eenheidverbergen')
    })
  }
  socketio.on('B2F_activiteit',function(jsonObject){
    htmlNieuws.innerHTML = jsonObject.boodschap
  })
}

const showCatData = function(jsonObject){
  let htmlString = ''
  if(jsonObject.details[0] == undefined){
    htmlString += `<tr class="c-data">
      <td>Geen Data...</td>
      </tr>`
  }else{
    for(let c of jsonObject.details){
      htmlString += `<tr class="c-data">
      <td>${c.datum}</td>
      <td>${c.totaal}</td>
      <td><span class="js-btn c-button" data-datum="${c.datum}" data-cat="${c.cat_id}">Verwijderen</span></td>
      </tr>`
    }
  }
    htmlTable.innerHTML = htmlString
    verwijderData()
}

const verwijderData = function(){
  const btn = document.querySelectorAll('.js-btn')
  for(let b of btn){
    b.addEventListener('click', function(){
      const body = JSON.stringify({"datum":this.getAttribute('data-datum')})
      handleData(`http://127.0.0.1:5000/api/v1/categories/${this.getAttribute('data-cat')}/data/`, showSucces, showError, 'DELETE', body)
    })
  }
}

const showSucces = function(jsonObject){
  htmlReport.innerHTML = `Er werden ${jsonObject.details} records verwijderd in de databank`
  const urlParams = new URLSearchParams(window.location.search);
  handleData(`http://127.0.0.1:5000/api/v1/categories/${urlParams.get('cat_id')}/data/`, showCatData, showError)
}

const showError = function(jsonObject){
  console.error(jsonObject)
}

const init = function () {
  console.info('DOM geladen');
  //html elementen ophalen van index.html
  htmlTiles = document.querySelector('.js-tiles');
  htmlNieuws = document.querySelector('.js-nieuws');
  //html elementen ophalen van report.html
  htmlTable = document.querySelector('.js-table');
  htmlReport = document.querySelector('.js-report');
  if(htmlTiles){
    handleData('http://127.0.0.1:5000/api/v1/categories/', showAllCat, showError)
  } else if(htmlReport){
    const urlParams = new URLSearchParams(window.location.search);
    if(urlParams == 0){
      window.location.href = 'index.html';
    } else{
      handleData(`http://127.0.0.1:5000/api/v1/categories/${urlParams.get('cat_id')}/data/`, showCatData, showError)
    }
  }

};

document.addEventListener('DOMContentLoaded', init);
