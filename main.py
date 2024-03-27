from random import randint
import copy
from flask import Flask, redirect, url_for, request, make_response, send_file, jsonify
users={}
games={}



from uuid import uuid4
from flask_json import FlaskJSON, as_json



def createCards():
    id=1
    cards=[]
    for color in range(1,4):
        for shape in range(1,4):
            for fill in range(1,4):
                for count in range(1,4):
                    cards.append({'id':id,'color':color,'shape':shape,'fill':fill,'count':count})
                    id+=1
    return cards
def createField(cards):
    field=[]
    for i in range(9):
        x=randint(0,len(cards))
        field.append(cards.pop(x))
    return field,cards
def renewField(field,cards,id1,id2,id3):

    for i in range(len(field)):
        if field[i]['id']==id1 or field[i]['id']==id2 or field[i]['id']==id3:
            x = randint(0, len(cards))
            field[i]==cards.pop(x)

    return field,cards
def addCards(field,cards):
    for i in range(3):
        x = randint(0, len(cards))
        field.append(cards.pop(x))
    return field, cards

# обьявляем наши ошибки
class CustomError(Exception):
   pass
class AuthError(Exception):
   pass
class NotFindError(Exception):
   pass


app = Flask(__name__)


def checkArgs(arguments):
   def args(func):
       def wrapper(*args, **kwargs):


          if set(arguments)==set(request.args.keys()):


               result = func(*args, **kwargs)
          else:
              raise CustomError('ошибка в переданных аргументах')


          return result


       wrapper.__name__ = func.__name__
       return wrapper
   return args




def auth(func):
   def wrapper(*args, **kwargs):
       tokens=users.keys()
       print(tokens)
       token = request.args.get('accessToken')
       print(token)
       if token in tokens:
           result = func(*args, **kwargs)
       else:
           raise AuthError('Пользователь не авторизованн - токен не подошел')
       return result


   wrapper.__name__ = func.__name__
   return wrapper
def errors(func):
   def wrapper(*args, **kwargs):
       try:
           try:
               result = func(*args, **kwargs)
               result.update({ "success": True, "exception": None})
               return result,200
           except Exception as err:
               response = {"success": False, "exception": {"message": str(err)}}  # написали ошибку
               raise

           print(resource)
       except AuthError :
           return response, 401
       except NotFindError :
           return response, 404
       except CustomError :
           return response, 400
       except Exception:
           raise
   wrapper.__name__ = func.__name__
   return wrapper


@app.route('/user/register', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['nickname','password'])
def register():

           nickname= request.args.get('nickname')
           password= request.args.get('password')
           rand_token = uuid4()
           users.update({str(rand_token):{'nick':nickname,'passwd':password,'gameId':None}})
           response={'nicname':nickname,'token':rand_token}
           return response

@app.route('/set/room/list', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['accessToken'])
@auth
def list():
           ids=[]
           for id in games.keys():
            ids.append({'id':id})
           response={'games':ids}
           return response

@app.route('/set/room/enter', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['accessToken','gameId'])
@auth
def enter():
    id = int(request.args.get('gameId'))
    if int(id) in games.keys():
        response={
            "gameId": id
            }
        games[id]['users'].update({request.args.get('accessToken'):{'name':users[request.args.get('accessToken')]['nick'],'score':0}})
        users[request.args.get('accessToken')]['gameId']=int(id)

    else:
        raise NotFindError()


    return response



@app.route('/set/room/create', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['accessToken'])
@auth
def create():
    token=request.args.get('accessToken')
    cards=createCards()
    field,cards=createField(cards)
    if len(games.keys())==0:
        id=0
    else:
        id=max(games.keys())+1
    games.update({id:{'field':field,'cards':cards,'status':'ongoing','users':{token:{'name':users[token]['nick'],'score':0}}}})
    response = {
            "gameId": id
        }
    return response
@app.route('/set/add', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['accessToken'])
@auth
def add():
    id = users[request.args.get('accessToken')]['gameId']
    cards=games[id]['cards']
    field=games[id]['field']
    field,cards=addCards(field,cards)
    games[id]['cards']=cards
    games[id]['field']=field

    response = {

        }
    return response
@app.route('/set/scores', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['accessToken'])
@auth
def scores():
    id = users[request.args.get('accessToken')]['gameId']


    response = {
        "users":games[id]['users']
        }
    return response

@app.route('/set/field', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['accessToken'])
@auth
def field():
    id = users[request.args.get('accessToken')]['gameId']
    field=games[id]['field']

    response = {
        "field":field
        }
    return response

@app.route('/set/pick', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['accessToken','cards'])
@auth
def pick():
    cardsPick = request.args.get('cards').replace('[','').replace(']','').split(',')
    id = users[request.args.get('accessToken')]['gameId']
    cards=games[id]['cards']
    field = games[id]['field']
    for card in cardsPick:
        card=int(card)

    field1=field
    print(field)



    cardsD =copy.deepcopy(field)
    for carded in cardsD:
        del carded['id']



    sets=[]

    print(field)




    for i in range(len(field)):
        for j in range(i + 1, len(field)):
            card = field[i]
            card2 = field[j]
            print(card)

            defCard = {

                "color": 3,
                "shape": 3,
                "fill": 2,
                "count": 3
            }

            for key in defCard.keys():
                if card[key] != card2[key]:
                    defCard[key] = 6 - card[key] - card2[key]
                else:
                    defCard[key] = card[key]

            if defCard in cardsD:
                if card['id'] not in sets:
                    sets.append(str(card['id']))
                if card2['id'] not in sets:
                    sets.append(str(card2['id']))
    print(set(sets[:3]),set(cardsPick))
    if set(sets[:3])==set(cardsPick):
        isSet=True

        field,cards=renewField(field,cards,cardsPick[0],cardsPick[1],cardsPick[2])
        games[id]['cards'] = cards
        games[id]['field'] = field
        games[id][users][request.args.get('accessToken')]['score']+=3
    else:
        isSet=False


    response = {
        "isSet":isSet
        }
    if len(cards)<9:
        games[id]['status']='ended'
        for user in users:
            if int(user['gameId'])==int(id):
                user['gameId']=None
    return response



@app.route('/getData2', methods=['GET'])
@as_json
@errors
@checkArgs(arguments=['token','img'])

def getData2():  # put application's code here


       response={'data':'parampampam Data2','user':'copift',
                                      'password':'123'}# возвращаем данные
       return response






json = FlaskJSON(app)


app.config['JSON_AS_ASCII'] = False
app.config['JSON_ADD_STATUS'] = False


if __name__ == '__main__':
   app.run()
