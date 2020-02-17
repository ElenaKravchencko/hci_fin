from peewee import *
import datetime

db = SqliteDatabase('people.db')


class BaseModel(Model):
    class Meta:
        database = db


class Person(BaseModel):
    id = AutoField()
    name = CharField()
    email = CharField(null=True)


class Category(BaseModel):
    id = AutoField()
    title = CharField()
    limit = IntegerField(null=True)


class Buying(BaseModel):
    id = AutoField()
    shopname = CharField()
    date = DateTimeField()
    price = IntegerField()
    title = CharField(null=True)
    person = ForeignKeyField(Person, backref="buyings")  # one person has many buyings
    category = ForeignKeyField(Category, backref="buyings")  # one category has many buyings


class Goal(BaseModel):
    id = AutoField()
    title = CharField()
    dateCreation = DateField()
    dateToReach = DateField(null=True)
    current_amount = IntegerField()
    target_amount = IntegerField()
    person = ForeignKeyField(Person, backref="goals")  # one person has many goals


class Notification(BaseModel):
    id = AutoField()
    type = BooleanField(default=False)  # 1 - push; 0 - email
    text = CharField()
    date = DateField()
    goal = ForeignKeyField(Goal, backref="notifications", null=True)  # a goal may have many notifications


class Account(BaseModel):
    id = AutoField()
    title = CharField()
    current_amount = IntegerField()
    person = ForeignKeyField(Person, backref="accounts",
                             null=True)  # one user has many accounts - for savings, salary....


db.drop_tables([Person, Buying, Category, Account, Goal, Notification])

db.create_tables([Person, Buying, Category, Account, Goal, Notification])

user1 = Person.create(name="Popova Svetlana", email="ellenkrav@gmail.com")
user2 = Person.create(name="Ivanova Anna", email="ivanova@gmail.com")

supermarket = Category.create(title="supermarket")
restaurants = Category.create(title="restaurants")
transport = Category.create(title="transport")
gifts = Category.create(title="gifts")
auto = Category.create(title="auto")
apartments = Category.create(title="apartments")
clothes = Category.create(title="clothes")
beauty = Category.create(title="beauty")
health = Category.create(title="health")

Buying.create(shopname='rivegaushe', title='parfum', date=datetime.date(2020, 2, 2), price=2000, person=user1,
              category=Category.get(Category.title == 'beauty'))
Buying.create(shopname="drugstore", date=datetime.date(2020, 2, 1), price=700, person=user1,
              category=Category.get(Category.title == 'health'))
Buying.create(shopname="uniqlo", date=datetime.date(2020, 2, 10), price=2000, person=user2,
              category=Category.get(Category.title == 'clothes'))
Buying.create(shopname="okey", title='food for birthday', date=datetime.date(2020, 2, 14), price=4000, person=user1,
              category=Category.get(Category.title == 'supermarket'))
Buying.create(shopname="magnit", date=datetime.date(2020, 2, 15), price=1000, person=user2,
              category=Category.get(Category.title == 'supermarket'))
Buying.create(shopname='diksi', date=datetime.date(2020, 2, 2), price='750', person=user1,
              category=Category.get(Category.title == 'supermarket'))

autoGoal = Goal.create(title='auto', dateCreation=datetime.date(2020, 2, 1), dateToReach=datetime.date(2020, 7, 1),
                       current_amount=0, target_amount=500000, person=user1)

Notification.create(type=False, text='Do not forget to put 10000 on your savings account',
                    date=datetime.date(2020, 2, 13), goal=autoGoal)

Account.create(title='SberCardSalary', current_amount=60000, person=user1)
Account.create(title='MySavings', current_amount=100000, person=user1)
Account.create(title='Tinkoff', current_amount=30000, person=user2)

        #GOALS

def sendPushGoalReached(user):
    print('Push Notification was sent to ', user.name, 'with id= ', user.id)


def topUpGoalAmount(goal, sum):
    goal.current_amount += sum
    goal.save()
    if checkGoalReached(goal) == True:
        sendPushGoalReached(goal.person)


def checkGoalReached(goal):
    left = goal.target_amount - goal.current_amount
    if left <= 0:
        return True
    else:
        return False


def checkGoalLeft(goal):
    sumleft = goal.target_amount - goal.current_amount  # сколько осталось накопить
    daysPassed = (datetime.datetime.now().date() - goal.dateCreation).days
    tend = goal.current_amount / daysPassed  # как юзер копит, его тенденция
    daysLeft = (round(sumleft / tend))  # предположим, сколько ему нужно времени при такой тенденции
    return datetime.datetime.now().date() + datetime.timedelta(days=daysLeft)

        #STATISTICS

def getGeneralStatistics(user, dateStart, dateFinish):
    temp = []
    # найдем для юзера только его покупки и только те, что соответствуют периоду
    for i in Buying.select().where(
            ((Buying.date <= dateFinish).bin_and(Buying.date >= dateStart).bin_and(Buying.person == user1))):
        temp.append(i)
    # достанем из этого списка крайности и сумму для статистику
    maxBuying = max(temp, key=lambda item: item.price)
    minBuying = min(temp, key=lambda item: item.price)
    print('You,ve made', len(temp), ' buyings,',
          'the maximum price was', maxBuying.price, ' in the shop', maxBuying.shopname, 'category',
          maxBuying.category.title)
    print('The minimum price was', minBuying.price, 'rubles. It was in the shop', minBuying.shopname, 'category',
          minBuying.category.title)
    print('You,ve, spent in this period totally', sum(i.price for i in temp), 'rubles')


def viewBuyingsByCategory(user, category, dateStart, dateFinish):
    cat = Category.select().where(Category.title == 'supermarket')
    temp = []
    for i in Buying.select().where((Buying.category == cat).bin_and(Buying.person == user).bin_and(Buying.date >= dateStart).bin_and(Buying.date <= dateFinish)):
        temp.append(i)
    print('In this category (', category.title, ')', ' and period you have spent: ', sum(i.price for i in temp), sep='')
    for i in temp:
        if i.title is None:
            print(i.shopname, i.date, i.price)
        else:
            print(i.shopname, i.date, i.price, i.title)


def getAllCategoriesUserBuying(user, dateStart, dateFinish):
    res = Buying.select(Buying.category, Buying.price).where((Buying.person == user).bin_and(Buying.date >= dateStart).bin_and(Buying.date <= dateFinish))
    dict = {}

    for i in res:
        if dict.get(i.category) is None:
            dict[i.category] = i.price
        else:
            dict[i.category] += i.price
    return dict


            #USING FUNCTIONS

# если пользователь решил пополнить счет
topUpGoalAmount(autoGoal, 20000)

# если пользователь решил посмотреть, какпродвигается процесс накопления
if checkGoalLeft(autoGoal) > autoGoal.dateToReach:
    print('Unfortunately, if you will save this way,you will reach the goal at ', checkGoalLeft(autoGoal))
else:
    print('Keep going! You will reach your goal at time or earlier!')

# если пользователь решил посмотреть основную статистику за период
getGeneralStatistics(user1, datetime.date(2020, 2, 1), datetime.date(2020, 2, 29))

# если пользователь захотел посмотреть покупки в конкретной категории за период
viewBuyingsByCategory(user1, supermarket, datetime.date(2020, 2, 1), datetime.date(2020, 2, 29))

# И, НАКОНЕЦ, если пользователь захотел просмотреть траты по категориям за период
a = getAllCategoriesUserBuying(user1, datetime.date(2020, 2, 1), datetime.date(2020, 2, 29))
for i in a:
    print('category:', i.title, "spent:", a[i])
