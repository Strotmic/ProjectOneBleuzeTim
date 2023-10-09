const lanIP = `${window.location.hostname}:5000`;
const socketio = io(lanIP);
// const listenToUI = function () {};

const listenToSocket = function () {
  socketio.on('connect', function () {
    console.log('verbonden met socket webserver');
  });
};
// #region ***  DOM references                           ***********
// #endregion

let foodDetail,
  foodDetails,
  foodTable,
  foodCategories,
  foodTableCategorie,
  gewicht,
  wegen,
  history, 
  login,
  userID,
  submitBtn,
  goal,
  register,
  logout;

// #region ***  Callback-Visualisation - show___         ***********
const showError = function (error) {
  console.log(error);
};

const showFoodTable = function (x) {
  console.info(x);
  let htmlString = '<div class="c-table">   <div class="c-table--row2"> <div class="c-tac2"> <a class="js-add-food c-table--add"  href="addFood.html"> Eten Toevoegen </a>  </div>  </div>';
  for (let i of x) {
    console.info('tes');
    htmlString += `
                <div class="c-table--row">
                <p class="c-table--text">${i['tblName']} </p>
                <div class="c-smartphone">

                    <a class="c-table--btn" data-food="${i['foodID']}" href="foodDetail.html?foodID=${i.foodID}"> Details</a>
                    <a class="myButton c-table--btn" data-food=${i['foodID']} class="c-table--btn">Voeg 1 toe</a>

                </div>
            </div>`;

                                // <button data-food=${i['foodID']} class="js-wegen-eten c-table--btn">weeg en voeg toe</button>
  }
  htmlString+='</div>'
  document.querySelector('.js-foodTable').innerHTML = htmlString;
  listenToTable()
  listenToGewicht();
  listenToAddFoodTest();

  // showGewicht()
};

const listenToAddFoodTest = function(){
  x = document.querySelectorAll('.myButton')
  for(i of x){
    i.addEventListener("click", function () {
            document.getElementById('EerstePopup').classList.add("show");
            console.info(this.getAttribute('data-food'))
            localStorage.setItem('foodID',this.getAttribute('data-food'));

        });
  }

  y = document.querySelectorAll('.closePopup')
  for(i of y){
    i.addEventListener("click", function(){
          document.getElementById('TweedePopUp').classList.remove("show");
          document.getElementById('EerstePopup').classList.remove("show");
          document.getElementById('DerdePopup').classList.remove("show");
        })
  }
        //   document.getElementById('myButton').addEventListener("click", function () {
        //     document.getElementById('EerstePopup').classList.add("show");
        // });
        document.getElementById('VoegEenToe').addEventListener("click", function () {
            document.getElementById('EerstePopup').classList.remove("show");
            console.info(localStorage.getItem('foodID'))
            socketio.emit('F2B_add_food',[localStorage.getItem('foodID'),localStorage.getItem('userID'),0])
            document.getElementById('DerdePopup').classList.add("show");
        });
        document.getElementById('Weeg').addEventListener('click', function () {
            document.getElementById('EerstePopup').classList.remove("show");
            socketio.emit('F2B_start_wegen');
            document.getElementById('TweedePopUp').classList.add("show")
        });
        document.getElementById('tare').addEventListener("click", function () {
            console.info('Nu is hij getared')
            socketio.emit('F2B_tare')
            alert("De weegschaal is getared");
        });

        document.getElementById('weegEnVoegToe').addEventListener('click', function () {
            document.getElementById('TweedePopUp').classList.remove("show")
            alert("Het eten is toegevoegd");
            socketio.emit('F2B_add_food',[localStorage.getItem('foodID'),localStorage.getItem('userID')])
            document.getElementById('DerdePopup').classList.add("show")
        });
       document.getElementById('NogIetsToevoegen').addEventListener('click', function () {
            document.getElementById('DerdePopup').classList.remove("show")
            document.getElementById('EerstePopup').classList.add("show")
        })
        document.getElementById('Overzicht').addEventListener('click', function () {
            document.getElementById('DerdePopup').classList.remove("show")
                      window.location.href = `http://${window.location.hostname}:${location.port}/front/history.html`
        })
}

const showDetailFood = function (x) {
  console.info(x);
  let htmlString = `           <tr>
            <th>carboHydrates</th>
            <td>${x.carboHydrates}</td>
        </tr>
        <tr>
            <th>fiber</th>
            <td>${x.fiber}</td>
        </tr>
        <tr>
            <th>kcal</th>
            <td>${x.kcal}</td>
        </tr>
        <tr>
            <th>protein</th>
            <td>${x.protein}</td>
        </tr>
        <tr>
            <th>salt</th>
            <td>${x.salt}</td>
        </tr>
        <tr>
            <th>saturatedFat</th>
            <td>${x.saturatedFat}</td>
        </tr>
        <tr>
            <th>sugar</th>
            <td>${x.sugar}</td>
        </tr>
        <tr>
            <th>unsaturatedFat</th>
            <td>${x.unsaturatedFat}</td>
        </tr>
  `;
  document.querySelector('.js-foodDetail').innerHTML = htmlString;
  document.querySelector('.js-foodDetailLink').innerHTML= `<div class="c-detail">
                    <a class="myButton c-table--btn" data-food=${x['foodID']} class="c-table--btn">Voeg 1 toe</a>

                </div>`
  // listenToDetail();
    listenToTable()
    listenToAddFoodTest();
  listenToGewicht();
};

const showCategories = function (x) {
  console.info(`userID: ${localStorage.getItem('userID')}`)
  console.info(x);
  let htmlString = '<div class="c-categorie--item js-barcode"><a class="c-categorie--text" ">Scan item</a>  </div>';
  for (let i of x) {
    htmlString += `<div class="c-categorie--item"><a class="c-categorie--text" href="foodByCategorie.html?categorieID=${i.categorieID}">  ${i.name} </a>  </div>`;
  }
  htmlString += `<div class="c-categorie--item"><a class="c-categorie--text" href="foodTable.html"> All the food </a>  </div>`;
  foodCategories.innerHTML = htmlString;
  console.info(localStorage.getItem("userID"))
  let test = localStorage.getItem('userID')
  console.info(test)
  console.info(userID)
  // showGewicht();
  listenToBarcode()
  listenToPoweroff()
};

const showFoodByCategorie = function (x) {
  console.info(x[0].name);
  z=(document.querySelector('.js-name-categorie'))
  z.innerHTML=`<h2>${x[0].name}</h2>`
  let htmlString = '<div class="c-table--row2"><div class="c-tac2"> <a class="js-add-food c-table--add"  href="addFood.html"> Eten Toevoegen </a>  </div>  </div>';
  for (let i of x) {
    // console.info('tes');
    htmlString += `
                 <div class="c-table--row">
                <p class="c-table--text">${i['tblName']} </p>
                <div class="c-smartphone">

                    <a class="c-table--btn" data-food="${i['foodID']}" href="foodDetail.html?foodID=${i.foodID}"> Details</a>
                    <a class="myButton c-table--btn" data-food=${i['foodID']} class="c-table--btn">Voeg 1 toe</a>

                </div>
            </div>`;
  }
  foodTableCategorie.innerHTML = htmlString;
  listenToTable()
  listenToGewicht();
  listenToAddFoodTest();
  // showGewicht();
};

const showGewicht = function () {
  wegen.addEventListener('click', function () {
    console.info('clicked')
    socketio.emit('F2B_wegen', null);
    socketio.on('B2F_weging_gedaan', function (x) {
      console.info(x);
      gewicht.innerHTML = x.gewicht;
    });
  });
};

const showGoal = function(x){
  console.info(x[0])
  x=x[0]
  l=['kcal','protein','carboHydrates','fiber','unsaturatedFat','saturatedFat','sugar','salt']
   let html=`<form id="formElem2">
            <div class="c-form">
                <label for="DailyGoal">Daily Goal:</label>
                <select name="DailyGoal" id="DailyGoal">`
    for(i of l){
      if(i==x['goal']){
        html+=`<option selected value="${i}">${i}</option>`
      }else{
        html+=`<option value="${i}">${i}</option>`
      }
    }
      html+=`
                </select>
            </div>
            <div class="c-form">
                <label for="Amount">Amount:</label>
                <input value="${x['goalAmount']}" type="number" name="Amount" id="Amount" min="0">
            </div>
            <div class="c-form">
                <label for="Color">Kleur:</label>
                <input value="#${x['kleur']}" type="color" name="Color" id="Color">
            </div>
            <input class="js-submit-btn2" type="submit" value="Voeg Toe">
        </form>`
        goal.innerHTML=html;
        listenToChangeGoal()
}

const showHistory = function(x){
  console.info(x)
  try{
  let labels=[];
  let data=[];
  const keys = Object.keys(x[0]);  
  for(const i of x){
    console.log(i)
    labels.push(i.datum)
    data.push(i[`${keys[1]}`])
  }
  // console.info(data)
  drawHistory(labels,data, 'kcal')
  }catch(error){
    document.querySelector('.js-history').innerHTML='Er is nog geen historie'
    showDaily(0)
  }

}

const showDaily = function(x){
    // console.info(x['data'])
    // console.info('ok')
    // const labels = ['carbo hydrates','fiber','kcal','protein','salt','saturated fat',  'sugar','unsaturated fat' ]
    // let data =[]
    // for(let i of Object.values(x['data'])){
    //   console.info(i)
    //   data.push(i)
    // }
    // // if(length(data)==0){
    // //   console.info('Test')
    // // }
    // drawPie(labels, data)
    console.info(x)
    if(x==0){
      drawPie(['Nog geen data','Vandaag'],[1,1])
    }
    document.querySelector('.js-pie').innerHTML=''

    socketio.on('B2F_new_pie', function (x) {
      document.querySelector('.js-pie').innerHTML=''
      console.info(x);
      const labels=['Kcal','Protein','Fiber','Salt','Saturated fat','Unsaturated fat', 'Carbo Hydrates', 'Sugar']

      let data=[]
        for(let i of Object.values(x)){
        console.info(i)
        data.push(i)
    }
    drawPie(labels, data)
  });

    
}


// #endregion

// #region ***  Callback-No Visualisation - callback___  ***********
const drawPie = function(labels, data){
  console.info(data)
  console.info(labels)
var options = {

  colors: ['#ff6961', '#ffb480', '#f8f38d','#42d6a4','#08cad1','#59adf6','#9d94ff','#c780e8']
,
          series: data,
          chart: {
          width: 380,
          type: 'pie',
        },

        labels: labels,
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 200
            },
            legend: {
              position: 'bottom'
            }
          }
        }]
        };

        var chart = new ApexCharts(document.querySelector(".js-pie"), options);
        chart.render();
}

const drawHistory = function (labels, data, name) {
  console.info(data)
  console.info(labels)
  var options = {
          series: [{
          name: 'History',
          data: data
        }],
          chart: {
          height: 350,
          type: 'bar',
                   events: {
 dataPointSelection: function(event, chartContext, config) {
 console.log(config,config.selectedDataPoints[0][0], chartContext, config.w.config.xaxis.categories[config.selectedDataPoints[0][0]])
 socketio.emit('F2B_histogram_pie',[config.w.config.xaxis.categories[config.selectedDataPoints[0][0]],localStorage.getItem('userID')])
  }
 },
        },
        plotOptions: {
          bar: {
            borderRadius: 10,
            dataLabels: {
              position: 'top', // top, center, bottom
            },
          }
        },
        dataLabels: {
          enabled: false,
          formatter: function (val) {
            return val + ' '+name;
          },
          offsetY: -20,
          style: {
            fontSize: '12px',
            colors: ["#304758"]
          }
        },
        
        xaxis: {
          type:'datetime',
          categories: labels,
          position: 'top',
          axisBorder: {
            show: false
          },
          axisTicks: {
            show: false
          },
          crosshairs: {
            fill: {
              type: 'gradient',
              gradient: {
                colorFrom: '#D8E3F0',
                colorTo: '#BED1E6',
                stops: [0, 100],
                opacityFrom: 0.4,
                opacityTo: 0.5,
              }
            }
          },
          tooltip: {
            enabled: false,
          }
        },
        yaxis: {
          axisBorder: {
            show: false
          },
          axisTicks: {
            show: false,
          },
          labels: {
            show: true,
            formatter: function (val) {
              return val +' '+ name;
            }
          }
        
        },
        title: {
          text: 'Goal geschiedenis',
          floating: true,
          offsetY: 330,
          align: 'center',
          style: {
            color: '#444'
          }
        }
        };

  let chart = new ApexCharts(document.querySelector('.js-history'), options);
  chart.render();
  chart.zoomX(new Date,new Date);
};
// #endregion

// #region ***  Data Access - get___                     ***********
const getFoodTable = function () {
  handleData(`http://${lanIP}/api/v1/foodTable/`, showFoodTable, showError);
};

const getFoodDetail = function (id) {
  console.info(id);
  handleData(`http://${lanIP}/api/v1/foodDetail/${id}/`, showDetailFood, showError);
};

const getFoodCategories = function () {
  handleData(`http://${lanIP}/api/v1/foodCategories/`, showCategories, showError);
};
// #endregion

// #region ***  Event Listeners - listenTo___            ***********s
const listenToDetail = function(){
  const test = document.querySelector('.js-detail-add');
  console.info(test)
  test.addEventListener('click', function(){
    console.info('toegevoegd')
    const urlParams = new URLSearchParams(window.location.search);
    console.info(urlParams.get('foodID'))
    socketio.emit('F2B_add_food',[urlParams.get('foodID'),10])
  })
}

const listenToWegenFood = function(){

}

const listenToPoweroff = function(){
  document.querySelector('.js-poweroff').addEventListener('click', function(){
    if (confirm("Je zal het toestel afzetten")) {
  socketio.emit('F2B_poweroff');
} else {
  
}
    

  })
}

const listenToTable = function(){
  x = document.querySelectorAll('.js-add-food-table')
  for(const i of x){
    i.addEventListener('click', function(){
    console.info('toegevoegd')
    console.info(this.getAttribute('data-food'))
    socketio.emit('F2B_add_food',[this.getAttribute('data-food'),10,localStorage.getItem("userID")])
  })
  }
}
const showFood = function(data){
  console.log('toegevoegd')
  if(data.foodID>0){
    console.info('succesvol toegeovegd')
  }
}

const showGoal2 = function(data){
	console.log('goal changed')
	if(data.goalID>0){
	console.info('succesvol aangepast goal')
}
}

const listenToLogin = function(){
  console.info(localStorage.getItem('userID'))
  document.getElementById('formElemLogin').addEventListener('submit',(e)=>{
    e.preventDefault();
    let jsonObject={
      email:document.getElementById('email').value
    }
    socketio.emit('F2B_login',jsonObject);
  })
    socketio.on('B2F_login', function (x) {
      console.info(x);
      userID = localStorage.setItem("userID", x.userID);
      window.location.href = `http://${window.location.hostname}:${location.port}/front/categories.html`;
    });


  
}



const listenToGewicht=function(){
  x = document.querySelectorAll('.js-wegen-eten')
  for(const i of x){
    i.addEventListener('click', function(){
      console.info('pop-up')
      let txt;
        if (confirm("Leg uw eten op de weegschaal")) {
        console.info('weeg')
        let id = this.getAttribute('data-food')
        console.info(id)
        socketio.emit('F2B_weging', [id,localStorage.getItem("userID")]);
        socketio.on('B2F_weging_gedaan', function (y) {
        console.info(y);
        // gewicht.innerHTML = x.gewicht;
    });
      } else {
        txt = "You pressed Cancel!";
      }
    })
  }
}

const listenToChangeGoal=function(){
  let form = document.getElementById('formElem2')
  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    console.info()
    let jsonObject={
      dailyGoal: document.getElementById(`DailyGoal`).value,
	goalAmount: document.getElementById(`Amount`).value,
	kleur: document.getElementById(`Color`).value
    }
	url=`http://${lanIP}/api/v1/goal/${localStorage.getItem("userID")}/`
	handleData(url, showGoal2,showError,`POST`,JSON.stringify(jsonObject))
    alert('Goal succesvol aangepast')
  window.location.href = `http://${window.location.hostname}:${location.port}/front/categories.html`;
  })

}

const listenToRegister= function(){
  socketio.emit('F2B_login_uit')
  let form = document.getElementById('formElemRegister')
  form.addEventListener('submit', (e)=>{
    e.preventDefault()
    let jsonObject={
      naam: document.getElementById('Naam').value,
      voornaam: document.getElementById('VoorNaam').value,
      email:document.getElementById('Email').value,
      dailyGoal: document.getElementById('DailyGoal').value,
      amount: document.getElementById('Amount').value,
      color: document.getElementById('Color').value
    }
    socketio.emit('F2B_register', jsonObject)
    alert('Volg de instructies op het kleine scherm.')
    socketio.on('B2F_login', function (x) {
      console.info(x);
      userID = localStorage.setItem("userID", x.userID);
      window.location.href = `http://${window.location.hostname}:${location.port}/front/categories.html`;
    });
  })
}

const listenToLogOut = function (){
  console.log('logout')
  document.querySelector('.js-logout').addEventListener('click', function(){
    socketio.emit('F2B_logout',null)
    localStorage.setItem('userID',0)
    window.location.href = `http://${window.location.hostname}:${location.port}/front/`;
  })
}

const listenToBarcode=function(){
  document.querySelector('.js-barcode').addEventListener('click', function(){
    socketio.emit('F2B_barcode',[localStorage.getItem('userID')])
    console.info('barcode')
    alert('scan product')

    socketio.on('B2F_barcode_succes', function(x){
      console.info(x)
      console.info('barcode success')
      if(x){
        alert('Eten toegevoegd!')
      }
    })
  })
}

const listenToAddFood = function(){
let form = document.getElementById('formElem');
    form.addEventListener('submit', (e) =>{
      e.preventDefault();
        if(document.getElementById('iServing').value=='g'){
            portion = 100
        }else{
            portion = 1
        }
      let naam = document.getElementById('iNaam')
      let jsonObject={
          name : document.getElementById('iNaam').value,
          barcode : document.getElementById('iBarcode').value,
          categorie : document.getElementById('iCat').value,
          serving : document.getElementById('iServing').value,
          portionServing: portion,
          kcal : document.getElementById('iKcal').value,
          saturated : document.getElementById('iSat').value,
          unsaturated : document.getElementById('iUnsat').value,
          protein : document.getElementById('iProtein').value,
          carbo : document.getElementById('iCarbo').value,
          fiber : document.getElementById('iFiber').value,
          sugar : document.getElementById('iSugar').value,
          salt : document.getElementById('iSalt').value
          }
          url = `http://${lanIP}/api/v1/foodTable/`;
          handleData(url,showFood,showError,'POST', JSON.stringify(jsonObject))
          alert('eten is toegevoegd')
          window.location.href = `http://${window.location.hostname}:${location.port}/front/categories.html`;
    })
}
// #endregion

// #region ***  Init / DOMContentLoaded                  ***********

// #endregion
const init = function () {
  console.info('DOM geladen');
  login = document.querySelector('.js-login')
  foodTable = document.querySelector('.js-foodTable');
  details = document.querySelectorAll('.js-foodDetails');
  foodDetail = document.querySelector('.js-foodDetail');
  foodCategories = document.querySelector('.js-foodCategories');
  foodTableCategorie = document.querySelector('.js-foodTableCategorie');
  history = document.querySelector('.js-history')
  submitBtn = document.querySelector('.js-submit-btn')
  goal = document.querySelector('.js-goal-page')
  register = document.querySelector('.js-register-page')
  logout = document.querySelector('.js-poweroff')
  console.info(location.port)
  if(!login){
      listenToLogOut();
      
  }
  if(login){
      if(localStorage.getItem('userID')==0){
        listenToLogin();
      }else{
        window.location.href = `http://${window.location.hostname}:${location.port}/front/categories.html`;
      }


  }
  else if(register){
    listenToRegister();
  }
  else if (foodCategories) {
    getFoodCategories();
    gewicht = document.querySelector('.js-gewicht');
    wegen = document.querySelector('.js-wegen');
  } else if (foodTableCategorie) {
    const urlParams = new URLSearchParams(window.location.search);
    console.info(urlParams);
    handleData(
      `http://${lanIP}/api/v1/foodTable/${urlParams.get('categorieID')}/`,
      showFoodByCategorie,
      showError
    );
  } else if (foodTable) {
    getFoodTable();
  } else if (foodDetail) {
    const urlParams = new URLSearchParams(window.location.search);
    console.info(urlParams);
    handleData(
      `http://${lanIP}/api/v1/foodDetail/${urlParams.get('foodID')}/`,
      showDetailFood,
      showError
    );
  }else if (history){
    console.info('tes')
    handleData(`http://${lanIP}/api/v1/historyGoal/${localStorage.getItem("userID")}/`, showHistory, showError)
    handleData(`http://${lanIP}/api/v1/dailyGoal/${localStorage.getItem("userID")}/`, showDaily, showError)
  } else if(submitBtn){
    console.info('tesst')
    listenToAddFood()
  }else if(goal){
    handleData(`http://${lanIP}/api/v1/goal/${localStorage.getItem("userID")}/`, showGoal, showError)
  }
  // listenToUI();
  // listenToSocket();
};

document.addEventListener('DOMContentLoaded', init);
