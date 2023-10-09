from .Database import Database
from datetime import date, datetime

class DataRepository:


    @staticmethod
    def json_or_formdata(request):
        if request.method != 'GET' and request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    
    '''
    Everything about user
    '''

    @staticmethod
    def get_user_by_id(id):
        print(id)
        sql = 'select * from tblUser where userID=%s'
        params=[id]
        return Database.get_one_row(sql,params)
    
    @staticmethod
    def add_fingerprint(userID, print):
        sql='update tblUser set fingerScan=%s where userID=%s'
        params=[print, userID]
        Database.execute_sql(sql,params)

    @staticmethod
    def get_all_fingerprints():
        sql='select userID, fingerScan from tblUser'
        return Database.get_rows(sql)
    
    @staticmethod
    def get_emails():
         sql='select eMail,userID from tblUser'
         return Database.get_rows(sql)

    @staticmethod
    def get_kleur(userID):
        sql = 'select userID,kleur from tblUser where userID=%s'
        params=[userID]
        return Database.get_one_row(sql,params)
    
    @staticmethod
    def set_kleur(userID, kleur):
        sql='update tblUser set kleur=%s where userID=%s'
        params=[kleur,userID]
        Database.execute_sql(sql,params)
    
    @staticmethod
    def add_user(firstName,lastName,eMail,goalID,kleur):
        sql = 'insert into tblUser(firstName,lastName,eMail,goalID,kleur) values(%s,%s,%s,%s,%s)'
        params=[firstName,lastName,eMail,goalID,kleur]
        return Database.execute_sql(sql,params)

    @staticmethod
    def add_goal(goal,goalAmount):
         sql='insert into tblGoal(goal,goalAmount) values(%s,%s)'
         params = [goal, goalAmount]
         return Database.execute_sql(sql,params)

    @staticmethod
    def set_goal(userID, goal, goalAmount, description):
        sql = 'update tblGoal set goal=%s, goalAmount=%s, description=%s where goalID=(select userID from tblUser where userID=%s);'
        params=[goal, goalAmount, description, userID]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_goal(userID):
        # print('Dit si een test van get_goal')
        sql = 'select g.goal, g.goalAmount, u.kleur from tblGoal g join tblUser u on g.goalID=u.goalID where u.userID=%s;'
        params=[userID]
        return Database.get_rows(sql,params)
    
    '''
    everything about food
    '''

    @staticmethod
    def get_food_categories():
        sql ='select categorieID,name from tblCategorie'
        return Database.get_rows(sql)
    
    @staticmethod
    def add_new_categorie(name, description=''):
        sql='insert into tblCategory(name,description) values(%s,%s)'
        params=[name,description]
        Database.execute_sql(sql,params)

    @staticmethod
    def get_food_table():
        sql = 'select foodID, tblName, barCode from tblFood'
        return Database.get_rows(sql)

    @staticmethod
    def get_detail_food(id):
        sql='select * from tblFood where foodID=%s'
        params=[id]
        return Database.get_one_row(sql,params)

    @staticmethod
    def get_food_by_categorie(id):
        sql='select f.*,c.name from tblFood f join tblCategorie c where f.tblCategorie_categorieID=c.categorieID having f.tblCategorie_categorieID=%s'
        params=[id]
        return Database.get_rows(sql,params)

    @staticmethod
    def get_nieuwe_maaltijd(userID):
        sql = 'insert into tblMeal(day, tblUser_userID) values(%s,%s);'
        today = date.today()
        params=[today,userID]
        Database.execute_sql(sql, params)


    @staticmethod
    def add_food_to_meal(userID, foodID, gewicht=0):
        print(f'Food_meal {userID}')
        today = date.today()
        sql = 'select mealID from tblMeal where tblUser_userID=%s and day=%s;'
        params = [userID,today]
        print(f'Test van add_food_toMeal {params}')
        try:
            mealID = (Database.get_one_row(sql,params)['mealID'])
        except:
            sql = 'insert into tblMeal(day, tblUser_userID) values(%s,%s)'
            params=[today,userID]
            mealID=Database.execute_sql(sql,params)
        print(f'Dit is een mealid aangemaakt door repository{mealID}')
        current_time = datetime.now().strftime("%H:%M:%S")
        sql = 'insert into tblMeal_has_tblFood(tblMeal_mealID, tblFood_foodID, weight,hour) values(%s,%s,%s,%s);'
        params=[mealID,foodID,gewicht,current_time]
        return Database.execute_sql(sql,params)

    @staticmethod
    def add_food(tblName,barCode,tblCategorie_categorieID, serving='g', portionSering=100, kcal=0, saturatedFat=0, unsaturatedFat=0, protein=0, carboHydrates=0, fiber=0,sugar=0,salt=0):
        sql = 'insert into tblFood(tblName,barCode,tblCategorie_categorieID, serving, portionServing, kcal, saturatedFat, unsaturatedFat, protein, carboHydrates, fiber,sugar,salt) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        params = [tblName, barCode, tblCategorie_categorieID, serving, portionSering,
                  kcal, saturatedFat, unsaturatedFat, protein, carboHydrates, fiber, sugar, salt]
        return Database.execute_sql(sql,params)

    # @staticmethod

    '''
    HISTORIEK
    '''

    #
    #Aanapssen van goal
    #
    #
    @staticmethod
    def get_goal_by_user(id):
        sql = 'SELECT g.goal FROM weegschaal.tblGoal g join tblUser u on u.goalID=g.goalID where u.userID=%s;'
        params = [id]

        x = Database.get_one_row(sql, params)['goal']
        # print(x)
        # {'goal': 'kcal'}
        # print(x['goal'].strip(" \' "))
        if x == 'kcal':
                    # print('ok')
                    sql = 'select f.kcal as"goal", mf.weight as "weight", f.serving as "serving", f.portionServing as"portionServing" from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on foodID=mf.tblFood_foodID where u.userID=%s and m.day=%s;'
                    today = date.today()
                    # print(today)
                    params = [id, today]
                    return Database.get_rows(sql, params)
            
            
        elif x == 'protein':
                    sql = 'select f.kcal as"goal", mf.weight as "weight", f.serving as "serving", f.portionServing as"portionServing" from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on foodID=mf.tblFood_foodID where u.userID=%s and m.day=%s;'
                    today = date.today()
                    # print(today)
                    params = [id, today]
                    return Database.get_rows(sql, params)
            
            
        elif x == 'fiber':
                    sql = 'select f.kcal as"goal", mf.weight as "weight", f.serving as "serving", f.portionServing as"portionServing" from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on foodID=mf.tblFood_foodID where u.userID=%s and m.day=%s;'
                    today = date.today()
                    # print(today)
                    params = [id, today]
                    return Database.get_rows(sql, params)
            
            
        elif x == 'salt':
                    sql = 'select f.kcal as"goal", mf.weight as "weight", f.serving as "serving", f.portionServing as"portionServing" from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on foodID=mf.tblFood_foodID where u.userID=%s and m.day=%s;'
                    today = date.today()
                    # print(today)
                    params = [id, today]
                    return Database.get_rows(sql, params)
            
            
        elif x == 'saturatedFat':
                    sql = 'select f.kcal as"goal", mf.weight as "weight", f.serving as "serving", f.portionServing as"portionServing" from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on foodID=mf.tblFood_foodID where u.userID=%s and m.day=%s;'
                    today = date.today()
                    # print(today)
                    params = [id, today]
                    return Database.get_rows(sql, params)
            
            
        elif x == 'unsaturatedFat':
                    sql = 'select f.kcal as"goal", mf.weight as "weight", f.serving as "serving", f.portionServing as"portionServing" from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on foodID=mf.tblFood_foodID where u.userID=%s and m.day=%s;'
                    today = date.today()
                    # print(today)
                    params = [id, today]
                    return Database.get_rows(sql, params)
            
            
        elif x == 'carboHydrates':
                    sql = 'select f.kcal as"goal", mf.weight as "weight", f.serving as "serving", f.portionServing as"portionServing" from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on foodID=mf.tblFood_foodID where u.userID=%s and m.day=%s;'
                    today = date.today()
                    # print(today)
                    params = [id, today]
                    return Database.get_rows(sql, params)
            
            
        elif x == 'sugar':
                    sql = 'select f.kcal as"goal", mf.weight as "weight", f.serving as "serving", f.portionServing as"portionServing" from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on foodID=mf.tblFood_foodID where u.userID=%s and m.day=%s;'
                    today = date.today()
                    # print(today)
                    params = [id, today]
                    return Database.get_rows(sql, params)

    @staticmethod
    def get_daily_from_user(id):
        sql = "select sum(f.kcal) as'Kcal', sum(f.protein) as'Protein', sum(fiber) as'Fiber', sum(salt) as'Salt', sum(saturatedFat)'Saturated fat', sum(unsaturatedFat) as'Unsaturated fat', sum(carboHydrates) as'Carbo Hydrates',sum(sugar) as'Sugar' from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s group by m.day having m.day=%s;"
        today = date.today()
        # print(today)
        params = [id, today]
        return Database.get_one_row(sql, params)

    @staticmethod
    def get_history_goal(id):
        sql = "select m.day as'dateum', sum(f.kcal) as'Kcal', sum(f.protein) as'Protein', sum(fiber) as'Fiber', sum(salt) as'Salt', sum(saturatedFat)'Saturated fat', sum(unsaturatedFat) as'Unsaturated fat', sum(carboHydrates) as'Carbo Hydrates',sum(sugar) as'Sugar' from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s group by m.day;"
        params = [id]
        return Database.get_rows(sql, params)


    #AAnpassen van keuze goal
    #
    #
    #
    @staticmethod
    def get_history_by_goal(userID):
        sql = 'select g.goal, g.goalAmount from tblGoal g join tblUser u on u.goalID=g.goalID where u.userID=%s'
        params = [userID]
        x = Database.get_one_row(sql, params)['goal']
        if x == 'kcal':
            sql = "select mf.weight , m.day as'datum', f.kcal as'kcal', f.serving, f.portionServing from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s"
            params = [userID]
            return Database.get_rows(sql, params)
        elif x=='protein':
            sql = "select mf.weight , m.day as'datum', f.protein as'protein', f.serving, f.portionServing from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s"
            params = [userID]
            return Database.get_rows(sql, params)
        elif x == 'fiber':
            sql = "select mf.weight , m.day as'datum', f.fiber as'Fiber', f.serving, f.portionServing from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s"
            params = [userID]
            return Database.get_rows(sql, params)
        elif x == 'salt':
            sql = "select mf.weight , m.day as'datum', f.salt as'Salt', f.serving, f.portionServing from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s"
            params = [userID]
            return Database.get_rows(sql, params)
        elif x == 'saturatedFat':
            sql = "select mf.weight , m.day as'datum', f.saturatedFat as'saturated Fat', f.serving, f.portionServing from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s"
            params = [userID]
            return Database.get_rows(sql, params)
        elif x == 'unsaturatedFat':
            sql = "select mf.weight , m.day as'datum', f.unsaturatedFat as'unsaturated Fat', f.serving, f.portionServing from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s"
            params = [userID]
            return Database.get_rows(sql, params)
        elif x == 'carboHydrates':
            sql = "select mf.weight , m.day as'datum', f.carboHydrates as'carbo Hydrates', f.serving, f.portionServing from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s"
            params = [userID]
            return Database.get_rows(sql, params)
        elif x == 'sugar':
            sql = "select mf.weight , m.day as'datum', f.sugar as'sugar', f.serving, f.portionServing from tblMeal_has_tblFood mf join tblMeal m on m.mealID=mf.tblMeal_mealID join tblUser u on u.userID=m.tblUser_userID join tblFood f on f.foodID=mf.tblFood_foodID where u.userID=%s"
            params = [userID]
            return Database.get_rows(sql, params)

    @staticmethod
    def get_all_food_user_daily(id ,day=0):
        sql = 'select m.mealID from tblMeal m join tblUser u on u.userID=m.tblUser_userID where u.userID=%s and m.day=%s'
        today=0
        if day == 0:
            today = date.today()
        else : today=day
        params = [id,today]
        print('Dit si de today van get al fod')
        print(today)
        print(id)
        x = Database.get_one_row(sql,params)
        print(x)
        sql = 'select f.*, mf.weight from tblFood f join tblMeal_has_tblFood mf on mf.tblFood_foodID=f.foodID join tblMeal m on mf.tblMeal_mealID=m.mealID join tblUser u on u.userID=m.tblUser_userId where mealID=%s;'
        try:
            params=[x['mealID']]
            return Database.get_rows(sql,params)
        except: print('error bij get all food')

    @staticmethod
    def get_food_by_barcode(barcode):
        sql='select foodID from tblFood where barcode=%s'
        params=[barcode]
        return Database.get_one_row(sql,params)
    '''
    Add devices
    '''
    @staticmethod
    def add_meting(deviceID, actionID, value, commentary=''):
        date = datetime.now()
        sql = 'insert into tblHistory(actionDate, value, commentary, tblDevice_deviceID,tblAction_actionID) values(%s, %s,%s,%s,%s)'
        params = [date, value, commentary, deviceID, actionID]
        return Database.execute_sql(sql, params)
