import logging
from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import json
import random
from aiogram.utils.emoji import emojize
from urllib.request import urlopen
import requests

token = "1447798712:AAHm6uSknzWH1XZijZgWfc6tAPlWWyKtcOE"
logging.basicConfig(level=logging.INFO)

craneBot = Bot(token=token)
dp = Dispatcher(craneBot, storage=MemoryStorage())

location_request = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton(emojize(':world_map: Send your location.'), request_location=True)).add(KeyboardButton(emojize(':x: Cancel.')))

main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(emojize(':writing_hand: Send new crane.'))).add(KeyboardButton('Catch a crane.')).add(KeyboardButton(emojize(':envelope: Read a crane from the pocket.'))).add(KeyboardButton('Set new name.')).add(KeyboardButton(emojize(":world_map: Set the location.")))

remove = ReplyKeyboardRemove()

commands = ['Catch a crane.', emojize(':envelope: Read a crane from the pocket.'), emojize(':envelope: Read a crane from the pocket.'), 'Set new name.', emojize(":world_map: Set the location."), 'Cancel.']

SECRET_KEY = '$2b$10$FyaFZ3DqdWEHYUch0yU90uL.8prii18XOrTSgfC4L9hSMKzuzX6dq'
urls = {'users-info': 'https://api.jsonbin.io/b/5ff2711d14be5470601955bc', 'cranes': 'https://api.jsonbin.io/b/5ff27101a2070e409d6dcec0'}

headers = {'Content-Type': 'application/json', 'secret-key': '$2b$10$FyaFZ3DqdWEHYUch0yU90uL.8prii18XOrTSgfC4L9hSMKzuzX6dq', 'versioning': 'false'}

class User(StatesGroup):
	waiting_for_location = State()
	waiting_for_name = State()

class Crane(StatesGroup):
	waiting_for_crane_title = State()
	waiting_for_crane = State()
	waiting_for_catch = State()
	waiting_for_choice = State()
	dysplay_a_crane = State()

def get_place(lat, lon):
	url = f"http://api.geonames.org/countryCodeJSON?lat={lat}&lng={lon}&username=cute_skirt"
	print(url)
	j = json.loads(urlopen(url).read())
	country = j["countryName"]
	return country

def randper():
	return True if random.randint(1,100) > 30 else False

def gen():
	return "".join([random.choice([str(random.randint(0,10)), chr(random.randint(65,123))]) for _ in range(10)])

@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
	print(message)
	
	req = requests.get(urls['users-info'], headers=headers)
	users_info = json.loads(req.text)
	
	if str(message['from']['id']) in users_info.keys():
		await message.reply("What do you want now?", reply_markup=main_menu)
		requests.put(urls['users-info'], json=users_info, headers=headers)
		await state.finish()
		return
	else:
		users_info[str(message['from']['id'])] = {'country': "none", 'written-cranes': [], 'read-cranes': [], 'nick': "Incognito"}
		await state.finish()
	
	requests.put(urls['users-info'], json=users_info, headers=headers)
	
	await message.answer(emojize("Hi! I'm crane's coordinator :wink:, and I'll help you to srart. First, send me your location to know your country."), reply_markup = location_request)
	await User.waiting_for_location.set()


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def set_state(message: types.Message, state: FSMContext):
	text = message['text']
	if text == emojize(':writing_hand: Send new crane.'):
		cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Cancel.'))
		await message.answer('Write the title of letter.', reply_markup=cancel)
		await Crane.waiting_for_crane_title.set()
	if text == 'Catch a crane.':
		catch = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('Try.')).add(KeyboardButton('Later.')).add(KeyboardButton('Cancel.'))
		await message.answer(f'You have some {random.choice(["really bad", "good", "great", "low", "high"])} chanses to catch a paper crane....', reply_markup=catch)
		await Crane.waiting_for_catch.set()
	if text == emojize(':envelope: Read a crane from the pocket.'):
		req = requests.get(urls['users-info'], headers=headers)
		users_info = json.loads(req.text)

		if len(users_info[str(message['from']['id'])]['read-cranes']) == 0:
			await message.reply(emojize('You haven`t cought any paper crane, try it. :wink:'), reply_markup=main_menu)
			requests.put(urls['users-info'], json=users_info, headers=headers)
			return
		else:
			read_crane = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Choice from all cranes.')).add(KeyboardButton('Random crane.')).add(KeyboardButton('Cancel.'))
			await message.answer(emojize('Choose what you need - choice from all or random one? :face_with_monocle:'), reply_markup=read_crane)
			requests.put(urls['users-info'], json=users_info, headers=headers)
			await Crane.waiting_for_choice.set()
	if text == 'Set new name.':
		req = requests.get(urls['users-info'], headers=headers)
		users_info = json.loads(req.text)
		
		cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Cancel.'))
		
		await message.answer(f'Send me your new name. (current name: {users_info[str(message["from"]["id"])]["nick"]})', reply_markup=cancel)
		requests.put(urls['users-info'], json=users_info, headers=headers)
		await User.waiting_for_name.set()
	if text == emojize(":world_map: Set the location."):
		req = requests.get(urls['users-info'], headers=headers)
		users_info = json.loads(req.text)
		
		if users_info[str(message['from']['id'])]['country'] != "none":
			await state.finish()
			await message.reply(f'You`ve already set your location ({users_info[str(message["from"]["id"])]["country"]})', reply_markup=main_menu)
			requests.put(urls['users-info'], json=users_info, headers=headers)
		else:
			await message.answer(emojize("Send me your location to know your country. :world_map:"), reply_markup=location_request)
			requests.put(urls['users-info'], json=users_info, headers=headers)
			await User.waiting_for_location.set()

	if text == "Cancel.":
		await state.finish()
		await message.reply("What do you want now?", reply_markup=main_menu)

@dp.message_handler(state=User.waiting_for_name, content_types=types.ContentTypes.TEXT)
async def new_name(message: types.Message, state: FSMContext):
	if message['text'] == "Cancel.":
		await state.finish()
		await message.reply("What do you want now?", reply_markup=main_menu)
		return
	
	req = requests.get(urls['users-info'], headers=headers)
	users_info = json.loads(req.text)
	
	name = message['text']
	
	users_info[str(message['from']['id'])]['nick'] = name
	
	requests.put(urls['users-info'], json=users_info, headers=headers)
	
	await message.reply(emojize(f'Your name was successfully changed to {name}! :tada:'), reply_markup=main_menu)
	
	await state.finish()

@dp.message_handler(state=User.waiting_for_location, content_types=types.ContentTypes.LOCATION)
async def message_for_start(message: types.Message, state: FSMContext):
	try:		
		req = requests.get(urls['users-info'], headers=headers)
		users_info = json.loads(req.text)
		
		if users_info[str(message['from']['id'])]['country'] == "none":
			country = get_place(message.location["latitude"], message.location["longitude"])
			users_info[str(message['from']['id'])]['country'] = country
			requests.put(urls['users-info'], json=users_info, headers=headers)
			await message.reply(f"Congrats, cranes will fly to {country} and meet you soon.", reply_markup=main_menu)
		else:
			requests.put(urls['users-info'], json=users_info, headers=headers)
			await message.reply(emojize("You can't change your location. :pensive:"), reply_markup=main_menu)
	except:
		await message.reply(emojize("Sorry, but we have some troubles with your location right now, try later. :pensive:"), reply_markup=main_menu)
		
	await state.finish()

@dp.message_handler(state=Crane.waiting_for_choice, content_types=types.ContentTypes.TEXT)
async def choose_crane(message:types.Message, state: FSMContext):
	
	if message['text'] == "Cancel.":
		await state.finish()
		await message.reply("What do you want now?", reply_markup=main_menu)
		return
	
	req = requests.get(urls['users-info'], headers=headers)
	users_info = json.loads(req.text)
	
	read_cranes = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	
	req = requests.get(urls['cranes'], headers=headers)
	cranes = json.loads(req.text)
	
	global to_share
	to_share = {}
	
	for i in range(len(users_info[str(message['from']['id'])]['read-cranes'])):
		read_cranes.add(KeyboardButton(cranes['cranes'][users_info[str(message['from']['id'])]['read-cranes'][i]][0]))
		to_share[cranes['cranes'][users_info[str(message['from']['id'])]['read-cranes'][i]][0]] = users_info[str(message['from']['id'])]['read-cranes'][i]
	read_cranes.add('Cancel.')
	
	if message['text'] == 'Random crane.':
		yes = random.choice(list(to_share.values()))
		await message.reply(f'{cranes["cranes"][yes][0]}'+'\n\n'+emojize(f'{cranes["cranes"][yes][-1]}'), reply_markup=main_menu)
		requests.put(urls['users-info'], json=users_info, headers=headers)
		requests.put(urls['cranes'], json=cranes, headers=headers)
		print(req.text)
		await state.finish()
	else:
		await state.update_data(cranes_=to_share)
		await message.answer('Choose a paper crane from menu.', reply_markup=read_cranes)
		requests.put(urls['users-info'], json=users_info, headers=headers)
		requests.put(urls['cranes'], json=cranes, headers=headers)
		print(req.text)
		await state.finish()
		await Crane.dysplay_a_crane.set()

@dp.message_handler(state=Crane.dysplay_a_crane, content_types=types.ContentTypes.TEXT)
async def dysplay(message: types.Message, state: FSMContext):

	if message['text'] == "Cancel.":
		await state.finish()
		await message.reply("What do you want now?", reply_markup=main_menu)
		return
	
	req = requests.get(urls['cranes'], headers=headers)
	cranes = json.loads(req.text)
	
	await message.reply(emojize(cranes['cranes'][to_share[message['text']]][-1]), reply_markup = main_menu)
	
	requests.put(urls['cranes'], json=cranes, headers=headers)
	
	await state.finish()

@dp.message_handler(state=Crane.waiting_for_catch, content_types=types.ContentTypes.TEXT)
async def catch(message: types.Message, state: FSMContext):
	if message['text'] in ["Cancel.", "Later."]:
		await state.finish()
		await message.reply("What do you want now?", reply_markup=main_menu)
		return
	
	if not randper():
		await message.reply(emojize('You can`t reach for flying paper cranes... :pensive: Try later.'), reply_markup = main_menu)
		await state.finish()
		return
	if message['text'] == 'Try.':
		req = requests.get(urls['users-info'], headers=headers)
		users_info = json.loads(req.text)
		
		req = requests.get(urls['cranes'], headers=headers)
		cranes = json.loads(req.text)
		
		crane_to_catch = ''
		
		for i in cranes['cranes']:
			if i not in users_info[str(message['from']['id'])]['read-cranes'] and i not in users_info[str(message['from']['id'])]['written-cranes']:
				crane_to_catch = i
				break
		
		if crane_to_catch == '':
			await message.reply(emojize('You can`t reach for flying paper cranes... :pensive: Try later.'), reply_markup = main_menu)
			await state.finish()
			return
		
		users_info[str(message['from']['id'])]['read-cranes'].append(crane_to_catch)
		
		requests.put(urls['users-info'], json=users_info, headers=headers)
		
		await message.reply(f'{cranes["cranes"][crane_to_catch][0]}'+'\n\n'+emojize(f'{cranes["cranes"][crane_to_catch][-1]}'), reply_markup=main_menu)
		requests.put(urls['cranes'], json=cranes, headers=headers)
		print(req.text)
		await state.finish()
	else:
		await message.reply(emojize('Use only commands from menu, please! :sob:'))
		await state.finish()

@dp.message_handler(state=Crane.waiting_for_crane_title, content_types=types.ContentTypes.TEXT)
async def crane_title(message: types.Message, state: FSMContext):
	if message['text'] in commands:
		if message['text'] == 'Cancel.':
			await state.finish()
			await message.reply("What do you want now?", reply_markup=main_menu)
			return
		await state.finish()
		await message.reply(emojize("Do not use commands as titles, please! :sob:"), reply_markup=main_menu)
		return
	
	if len(message['text']) > 64:
		await message.reply('Don`t write long titles, please! Type your title again.')
		await Crane.waiting_for_crane_title.set()
		return
	
	global title___
	title___ = message['text']
	cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Cancel.'))
	await message.reply('Title has been successfully chosen, write the paper crane`s text now.', reply_markup=cancel)
	await Crane.waiting_for_crane.set()

@dp.message_handler(state=Crane.waiting_for_crane, content_types=types.ContentTypes.TEXT)
async def crane_text(message: types.Message, state: FSMContext):
	if message['text'] == "Cancel.":
		await state.finish()
		await message.reply("What do you want now?", reply_markup=main_menu)
		return
	
	req = requests.get(urls['users-info'], headers=headers)
	users_info = json.loads(req.text)
	
	req = requests.get(urls['cranes'], headers=headers)
	cranes = json.loads(req.text)
	
	code = gen()
	
	users_info[str(message['from']['id'])]['written-cranes'].append(code)
	
	title = title___
	
	new_text = message['text']+'\n'+f'by {users_info[str(message["from"]["id"])]["nick"]} from {users_info[str(message["from"]["id"])]["country"]}'
	
	cranes['cranes'][code] = [title, new_text]
	
	requests.put(urls['users-info'], json=users_info, headers=headers)
	
	requests.put(urls['cranes'], json=users_info, headers=headers)
	print(req.text)
	
	await message.reply('Your paper crane was sent on the other side of Earth.', reply_markup=main_menu)
	
	await state.finish()

executor.start_polling(dp, skip_updates=False)