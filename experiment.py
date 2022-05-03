'''
This test script needs the following files:
STR_SUMO.py, RouteController.py, Util.py, test.net.xml, test.rou.xml, myconfig.sumocfg and corresponding SUMO libraries.

If you are using Windows, you may need the Windows versions of STR_SUMO.py and target_vehicles_generation_protocols.py
	with '_win' appended to their filenames.
'''

import os
import sys
from xml.dom.minidom import parse, parseString
from core.Util import *
from controller.RouteController import *
from sumolib import checkBinary
import traci

if sys.platform.startswith('win'):
	sysos = 'Windows'
else:
	sysos = 'Unix'
print(sysos, "operating system detected")

if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("No environment variable SUMO_HOME!")

if sysos == 'Windows':
	from core.target_vehicles_generation_protocols_win import *
	from core.STR_SUMO_win import StrSumo
	configpath = "configurations\\"
else:
	from core.target_vehicles_generation_protocols import *
	from core.STR_SUMO import StrSumo
	configpath = "./configurations/"

usegui = 'nogui' not in str(sys.argv).lower()
conPre = '->'


# use vehicle generation protocols to generate vehicle list
def get_controlled_vehicles(route_filename, connection_info, \
	num_controlled_vehicles=10, num_uncontrolled_vehicles=20, pattern = 1):
	'''
	:param @route_filename <str>: the name of the route file to generate
	:param @connection_info <object>: an object that includes the map inforamtion
	:param @num_controlled_vehicles <int>: the number of vehicles controlled by the route controller
	:param @num_uncontrolled_vehicles <int>: the number of vehicles not controlled by the route controller
	:param @pattern <int>: one of four possible patterns. FORMAT:
			-- CASES BEGIN --
				#1. one start point, one destination for all target vehicles
				#2. ranged start point, one destination for all target vehicles
				#3. ranged start points, ranged destination for all target vehicles
			-- CASES ENDS --
	'''
	vehicle_dict = {}
	#print("Generating vehicles using network in", connection_info.net_filename) #
	print('Generating vehicles. . .')
	generator = target_vehicles_generator(connection_info.net_filename)

	# list of target vehicles is returned by generate_vehicles
	vehicle_list = generator.generate_vehicles(num_controlled_vehicles, num_uncontrolled_vehicles, \
		pattern, route_filename, connection_info.net_filename)

	for vehicle in vehicle_list:
		vehicle_dict[str(vehicle.vehicle_id)] = vehicle

	return vehicle_dict


def test_policy(vehicle_info, connection_info, sumo_binary, policy, runs=1):
	if usegui:
		if simGUI.get():
			print('Waiting for GUI. . .')
	
	total_time = 0
	end_number = 0
	deadlines_missed = 0
	for i in range(runs):
		if usegui:
			status1.set('Generating vehicle batch. . .')
		vehicles = get_controlled_vehicles(vehicle_info['route'], connection_info, vehicle_info['controlled'], vehicle_info['uncontrolled'], vehicle_info['pattern'])
		
		print('\nRunning simulation' + (' #' + str(i+1) if runs > 1 else '') + '. . .')
		if usegui:
			status1.set('Running simulation' + (' ' + str(i+1) + ' of ' + str(runs) if runs > 1 else '') + '. . .')
		
		total, end_num, missed = run_simulation(policy, vehicles, connection_info, sumo_binary)
		total_time += total
		end_number += end_num
		deadlines_missed += missed
		print('Done.\n')
	
	total_time = total_time / runs
	end_number = end_number / runs
	deadlines_missed = deadlines_missed / runs
	
	return total_time, end_number, deadlines_missed


def run_simulation(scheduler, vehicles, connection_info, sumo_binary):
	try:
		simulation = StrSumo(scheduler, connection_info, vehicles)
		
		traci.start([sumo_binary, "-c", "./configurations/myconfig.sumocfg", \
					 "--tripinfo-output", "./configurations/trips.trips.xml", \
					 "--fcd-output", "./configurations/testTrace.xml"])
		total_time, end_number, deadlines_missed = simulation.run()
		traci.close()
		
		return total_time, end_number, deadlines_missed
		
	except Exception as err:
		print("\n!!!  The following", str(type(err))[8:-2], "occurred while running the simulation:")
		try:
			if traci.isLoaded():
				traci.close()
		except Exception:
			pass
		raise err


## Functions related to the GUI ##
def name_checkbox_toggle():
	if sameName.get():
		policy.delete(0, 'end')
		policy.insert(0, controller.get())
		policy.state(['readonly'])
	else:
		policy.state(['!readonly'])

def sim_gui_checkbox_toggle():
	if simGUI.get():
		runs.state(['readonly'])
		runs.set(1)
		batchButton.state(['disabled'])
	else:
		runs.state(['!readonly'])
		batchButton.state(['!disabled'])

def update_policy_samename(event):
	if sameName.get():
		policy.state(['!readonly'])
		policy.delete(0, 'end')
		policy.insert(0, controller.get())
		policy.state(['readonly'])

def config_editor():
	runbutton.state(['disabled'])
	configButton.state(['disabled'])
	batchButton.state(['disabled'])
	
	def exit():
		runbutton.state(['!disabled'])
		configButton.state(['!disabled'])
		batchButton.state(['!disabled'])
		win.destroy()
	
	def save_config():
		with open(configpath + 'myconfig.sumocfg', 'w') as file:
			file.write(editor.get('1.0', 'end'))
		dom = parse(configpath + "myconfig.sumocfg")
		netfile['text'] = configpath + dom.getElementsByTagName('net-file')[0].attributes['value'].nodeValue
		routefile['text'] = configpath + dom.getElementsByTagName('route-files')[0].attributes['value'].nodeValue
		exit()
	
	# Creating UI window
	win = Toplevel(root)
	win.title('STR-SUMO Configuration Editor')
	
	# Creating text editor
	editor = Text(win)
	editor.grid(column=0, row=0)
	with open(configpath + 'myconfig.sumocfg', 'r') as file:
		editor.insert('1.0', file.read())
	
	# Creating buttons
	editorButtonFrame = ttk.Frame(win)
	editorButtonFrame.grid(column=0, row=1)
	ttk.Button(editorButtonFrame, text='Save and exit', command=save_config).grid(column=0, row=0)
	ttk.Button(editorButtonFrame, text='Exit', command=exit).grid(column=1, row=0)
	
	win.mainloop()

def batch_test_editor():
	runbutton.state(['disabled'])
	configButton.state(['disabled'])
	batchButton.state(['disabled'])
	guiCheck.state(['disabled'])
	nameCheck.state(['disabled'])
	controller.state(['disabled'])
	policy.state(['disabled'])
	runs['show'] = '-'
	controlled['show'] = '-'
	uncontrolled['show'] = '-'
	
	def exit():
		runbutton.state(['!disabled'])
		configButton.state(['!disabled'])
		batchButton.state(['!disabled'])
		guiCheck.state(['!disabled'])
		nameCheck.state(['!disabled'])
		controller.state(['!disabled'])
		policy.state(['!disabled'])
		runs['show'] = ''
		controlled['show'] = ''
		uncontrolled['show'] = ''
		win.destroy()
	
	def start_experiments():
		experiments = []
		i = 0
		while editor.get(str(i+1)+'.0', str(i+1)+'.end') != '':
			# Checking for non-numeric characters
			try:
				line = [int(x) for x in editor.get(str(i+1)+'.0', str(i+1)+'.end').split()]
			except ValueError:
				inputStatus.set('ERROR: Line ' + str(i+1) + ' contains an invalid character (only numbers and spaces are valid)')
				return
			
			# Checking if enough parameters were given
			if len(line) < 4:
				inputStatus.set('ERROR: Not enough parameters were specified on line ' + str(i+1) + ' (' + str(len(line)) + '/4 were given)')
				return
			
			# Checking if parameter values are in valid range
			for j in range(3):
				if line[j] < 1:
					inputStatus.set('ERROR: Value of line ' + str(i+1) + ', parameter ' + str(j+1) + ' must be > 0')
					return
			if line[3] not in (1, 2, 3):
				inputStatus.set('ERROR: Value of line ' + str(i+1) + ', parameter 4 must be 1, 2, or 3')
				return
			
			# Adding entry to experiment list
			experiments.append({})
			experiments[i]['runs'] = line[0]
			experiments[i]['vehicle_info'] = {'route':routefile['text'], 'controlled':line[1], 'uncontrolled':line[2], 'pattern':line[3]}
			i += 1
		
		# Checking if any experiments were specified
		if len(experiments) == 0:
			inputStatus.set('ERROR: You must specify at least 1 experiment')
			return
		
		# Checking if output file was specified
		if outputEntry.get() == '':
			inputStatus.set('ERROR: Result filename not specified')
			return
		
		# Starting experiments
		start_sim_thread(experiments, outputEntry.get())
		win.destroy()
	
	# Creating UI window
	win = Toplevel(root)
	win.title('Batch Experiment Input')
	
	ttk.Label(win, justify='center', text='Enter the parameters for each experiment on a separate line in the following format:\
		\n<number of times to run the simulation> <number of controlled vehicles> <number of uncontrolled vehicles> <pattern number>').grid(column=0, row=0)
	
	editor = Text(win)
	editor.grid(column=0, row=1)
	
	ttk.Label(win, justify='center', text='Experiments will run with these additional parameters:\
		\nNetwork file: ' + netfile['text'] + '\nRoute file: ' + routefile['text'] + '\n' \
		+ policy.get() + ' policy from ' + controller.get() + ' controller').grid(column=0, row=2)
	
	# Creating result file entry box
	editorFileFrame = ttk.Frame(win)
	editorFileFrame.grid(column=0, row=3)
	ttk.Label(editorFileFrame, text='Results will be saved to this file: ').grid(column=0, row=0)
	outputEntry = ttk.Entry(editorFileFrame, width=50)
	outputEntry.grid(column=1, row=0)
	
	# Generating default result filename
	i = 1
	while True:
		autofname = policy.get() + '_result_' + str(date.today().day) + '-' + str(date.today().month) + '-' + str(date.today().year) + '_' + str(i) + '.csv'
		try:
			with open(autofname, 'r') as file:
				i += 1
		except Exception as err:
			break
	outputEntry.insert(0, autofname)
	
	# Creating buttons
	editorButtonFrame = ttk.Frame(win)
	editorButtonFrame.grid(column=0, row=4)
	ttk.Button(editorButtonFrame, text='Run experiments', command=start_experiments).grid(column=0, row=0)
	ttk.Button(editorButtonFrame, text='Cancel', command=exit).grid(column=1, row=0)
	
	inputStatus = StringVar()
	ttk.Label(win, textvariable=inputStatus).grid(column=0, row=5)
	
	win.mainloop()
	
def test_policy_gui(experiments, resultfile=''):
	status0.set('')
	status1.set('Setting things up. . .')
	
	# Attempting to load policy controller module
	try:
		exec("from controller." + controller.get() + "Controller import *")
	except Exception as err:
		status1.set('Could not load controller, see console for details.')
		print("!!! Could not load policy controller module with the given name.")
		print('Reason: ' + str(type(err))[8:-2] + ': ' + str(err) + '\n')
		return
	
	# Disabling appropriate GUI widgets
	nameCheck.state(['disabled'])
	guiCheck.state(['disabled'])
	controller.state(['disabled'])
	policy.state(['disabled'])
	otherArgs.state(['disabled'])
	configButton.state(['disabled'])
	runs.state(['disabled'])
	controlled.state(['disabled'])
	uncontrolled.state(['disabled'])
	for w in patternRadio:
		w.state(['disabled'])
	runbutton.state(['disabled'])
	batchButton.state(['disabled'])
		
	def enable_widgets():
		# Re-enabling GUI widgets
		nameCheck.state(['!disabled'])
		guiCheck.state(['!disabled'])
		controller.state(['!disabled'])
		policy.state(['!disabled'])
		otherArgs.state(['!disabled'])
		configButton.state(['!disabled'])
		runs.state(['!disabled'])
		runs['show'] = ''
		controlled.state(['!disabled'])
		controlled['show'] = ''
		uncontrolled.state(['!disabled'])
		uncontrolled['show'] = ''
		for w in patternRadio:
			w.state(['!disabled'])
		runbutton.state(['!disabled'])
		batchButton.state(['!disabled'])
	
	# Loading appropriate SUMO binary
	if simGUI.get():
		sumo_binary = checkBinary('sumo-gui')
	else:
		sumo_binary = checkBinary('sumo')
	
	# Loading road network
	init_connection_info = ConnectionInfo(netfile['text'])
	print("Using network file", netfile['text'])
	print("Using route file", routefile['text'])
	
	# Attempting to create policy scheduler
	try:
		scheduler = eval(policy.get() + "Policy(init_connection_info, *otherArgs.get().split())")
	except Exception as err:
		status1.set('Could not load policy, see console for details.')
		print("!!! Could not load policy from the given controller.")
		print('Reason: ' + str(type(err))[8:-2] + ': ' + str(err) + '\n')
		enable_widgets()
	else:
		# Running simulation(s)
		status1.set('Starting simulation(s). . .')
		print("Testing " + policy.get() + " Algorithm Route Controller")
		if resultfile != '':
			with open(resultfile, 'w') as file:
				file.write('Experiment #,simulation runs,controlled vehicles,uncontrolled vehicles,pattern,average total runtime,average vehicle roadtime,average deadlines missed,average vehicles not reaching destination\n')
		errexps = 0
		for i in range(len(experiments)):
			if len(experiments) > 1:
				status0.set('Running experiment ' + str(i+1) + ' of ' + str(len(experiments)))
				print('-= Experiment #' + str(i+1) + ' =-')
			
			try:
				total_time, end_number, deadlines_missed = test_policy(experiments[i]['vehicle_info'], init_connection_info, sumo_binary, scheduler, experiments[i]['runs'])
			except Exception as err:
				status1.set('An error ocurred, see console for details.')
				print("!!! The following", str(type(err))[8:-2], "occurred while testing the policy:")
				print('\t' + str(type(err))[8:-2] + ': ' + str(err) + '\n')
				errexps += 1
				#enable_widgets()
				#raise(err)
				if resultfile != '':
					with open(resultfile, 'a') as file:
						file.write(','.join([str(i+1), str(experiments[i]['runs']), ','.join([str(x) for x in experiments[i]['vehicle_info'].values()][1:]), 'ERR,ERR,ERR,ERR\n']))

			else:
				if resultfile != '':
					with open(resultfile, 'a') as file:
						file.write(','.join([str(i+1), str(experiments[i]['runs']), ','.join([str(x) for x in experiments[i]['vehicle_info'].values()][1:]), str(total_time), ('N/A' if end_number == 0 else str(total_time/end_number)), str(experiments[i]['vehicle_info']['controlled'] - end_number + deadlines_missed), str(experiments[i]['vehicle_info']['controlled'] - end_number) + '\n']))
		
		if len(experiments) < 2:
			if errexps < 1:
				status0.set(('' if end_number > 0 else 'Something may have gone wrong; see console for details.\n') + \
				'Simulations complete! Results:\nAverage total simulation runtime: ' + str(total_time) + \
				'\nAverage vehicle roadtime: ' + ('N/A' if end_number == 0 else str(total_time/end_number)) + \
				'\nTotal vehicle number: ' + str(experiments[0]['vehicle_info']['controlled']) + \
				'\nAverage deadlines missed: ' + str(experiments[0]['vehicle_info']['controlled'] - end_number + deadlines_missed) + \
				'\nOn average, ' + str(experiments[0]['vehicle_info']['controlled'] - end_number) + ' vehicles could not reach their destinations.')
			else:
				status0.set('An error ocurred, see console for details.')
		else:
			statmsg = 'All ' + str(len(experiments)) + ' experiments completed.'
			if errexps > 0:
				statmsg += ('\n' + str(errexps) + ' experiments encountered errors (see console for details)')
			status0.set(statmsg)
		
		status1.set('' if resultfile == '' else ('Results saved to ' + resultfile))
		enable_widgets()

def start_sim_thread(experiments, resultfile):
	simThread = threading.Thread(target=test_policy_gui, args=(experiments, resultfile))
	simThread.start()

def start_experiment():
	experiments = [{}] 
	experiments[0]['vehicle_info'] = {'route':routefile['text'], 'controlled':int(controlled.get()), 'uncontrolled':int(uncontrolled.get()), 'pattern':patternChoice.get()}
	experiments[0]['runs'] = int(runs.get())
	start_sim_thread(experiments, 'lastresults.csv')


if __name__ == "__main__":
	## Parsing config file ##
	dom = parse(configpath + "myconfig.sumocfg")
	net_file = configpath + dom.getElementsByTagName('net-file')[0].attributes['value'].nodeValue
	route_file = configpath + dom.getElementsByTagName('route-files')[0].attributes['value'].nodeValue
	
	if usegui: ## Running program with GUI ##
		from tkinter import *
		from tkinter import ttk
		from tkinter.ttk import *
		import threading
		from datetime import date
		
		# Creating window
		root = Tk()
		root.title('Traffic Policy Tester')
		rootframe = ttk.Frame(root, padding=10)
		rootframe.grid()
		#rootframe.grid_anchor('n')
		#rootframe.grid_columnconfigure(index='all', weight=0)
		
		left = ttk.Frame(rootframe)
		left.grid(column=0, row=0)
		
		ttk.Separator(rootframe, orient='vertical').grid(column=1, row=0, ipady='2c', padx=1, sticky='ns')
		
		middle = ttk.Frame(rootframe)
		middle.grid(column=2, row=0)
		
		ttk.Separator(rootframe, orient='vertical').grid(column=3, row=0, ipady='2c', padx=1, sticky='ns')
		
		right = ttk.Frame(rootframe)
		right.grid(column=4, row=0)
		
		
		# Option/config widgets
		snFrame = ttk.Frame(left)
		snFrame.grid(column=0, row=0)
		ttk.Label(snFrame, text="Controller name same as policy name:").grid(column=0, row=0)
		sameName = BooleanVar()
		nameCheck = ttk.Checkbutton(snFrame, onvalue=True, offvalue=False, variable=sameName, command=name_checkbox_toggle)
		nameCheck.grid(column=1, row=0)
		
		sgFrame = ttk.Frame(left)
		sgFrame.grid(column=0, row=1)
		ttk.Label(sgFrame, text="Show simulation GUI:").grid(column=0, row=0)
		simGUI = BooleanVar()
		guiCheck = ttk.Checkbutton(sgFrame, onvalue=True, offvalue=False, variable=simGUI, command=sim_gui_checkbox_toggle)
		guiCheck.grid(column=1, row=0)
		
		configButton = ttk.Button(left, text='Edit config file', command=config_editor)
		configButton.grid(column=0, row=2)
		
		
		# Simulation environment options
		cframe = ttk.Frame(middle)
		cframe.grid(column=0, row=0)
		ttk.Label(cframe, text='Controller name:', justify='right').grid(column=0, row=0)
		controller = ttk.Combobox(cframe, values=[f[0:-13] for f in os.listdir('controller') if os.path.isfile(os.path.join('controller', f)) and f[-13:] == 'Controller.py'])
		controller.insert(0, 'Route')
		controller.grid(column=1, row=0)
		controller.state(['readonly'])
		controller.bind('<<ComboboxSelected>>', update_policy_samename)
		ttk.Label(cframe, text='Controller', anchor='w').grid(column=2, row=0)
		
		pFrame = ttk.Frame(middle)
		pFrame.grid(column=0, row=1)
		ttk.Label(pFrame, text='Policy:').grid(column=0, row=0)
		policy = ttk.Entry(pFrame)
		policy.insert(0, 'Random')
		policy.grid(column=1, row=0)
		ttk.Label(pFrame, text='Policy').grid(column=2, row=0)
		
		aFrame = ttk.Frame(middle)
		aFrame.grid(column=0, row=2)
		ttk.Label(aFrame, text='Additional policy arguments:').grid(column=0, row=0)
		otherArgs = ttk.Entry(aFrame)
		otherArgs.grid(column=1, row=0)
		
		nfFrame = ttk.Frame(middle)
		nfFrame.grid(column=0, row=3)
		ttk.Label(nfFrame, text='Network file: ').grid(column=0, row=0)
		netfile = ttk.Label(nfFrame, text=net_file)
		netfile.grid(column=1, row=0)
		
		rfFrame = ttk.Frame(middle)
		rfFrame.grid(column=0, row=4)
		ttk.Label(rfFrame, text='Route file:').grid(column=0, row=0)#(column=0, row=1)
		routefile = ttk.Label(rfFrame, text=route_file)
		routefile.grid(column=1, row=0)
		
		
		# Experiment parameter options
		rFrame = ttk.Frame(right)
		rFrame.grid(column=0, row=0)
		ttk.Label(rFrame, text='Simulations to run:').grid(column=0, row=0)
		runs = ttk.Spinbox(rFrame, from_=1, to=float('Inf'), width=4)
		runs.grid(column=1, row=0)
		runs.set(1)
		
		cvFrame = ttk.Frame(right)
		cvFrame.grid(column=0, row=1)
		ttk.Label(cvFrame, text='Vehicles controlled by policy:').grid(column=0, row=0)
		controlled = ttk.Spinbox(cvFrame, from_=1, to=float('Inf'), width=4)
		controlled.grid(column=1, row=0)
		controlled.set(10)
		
		ncvFrame = ttk.Frame(right)
		ncvFrame.grid(column=0, row=2)
		ttk.Label(ncvFrame, text='Vehicles NOT controlled by policy:').grid(column=0, row=0)
		uncontrolled = ttk.Spinbox(ncvFrame, from_=1, to=float('Inf'), width=4)
		uncontrolled.grid(column=1, row=0)
		uncontrolled.set(50)
		
		pattFrame = ttk.Frame(right)
		pattFrame.grid(column=0, row=3)
		ttk.Label(pattFrame, text='Start/destination pattern').grid(column=0, row=0)
		patternChoice = IntVar()
		patternChoice.set(1)
		patternRadio = []
		patternRadio.append(ttk.Radiobutton(pattFrame, text='1', value=1, variable=patternChoice))
		patternRadio.append(ttk.Radiobutton(pattFrame, text='2', value=2, variable=patternChoice))
		patternRadio.append(ttk.Radiobutton(pattFrame, text='3', value=3, variable=patternChoice))
		for i in range(len(patternRadio)):
			patternRadio[i].grid(column=i+1, row=0)
		
		batchButton = ttk.Button(right, text='Run multiple experiments', command=batch_test_editor)
		batchButton.grid(row=4)
		
		
		# Simulation status1 widgets
		buttonFrame = ttk.Frame(middle)
		buttonFrame.grid(column=0, row=6)
		runbutton = ttk.Button(buttonFrame, text='Run', command=start_experiment)
		runbutton.grid(column=0, row=0)
		ttk.Button(buttonFrame, text="Quit", command=root.destroy).grid(column=1, row=0)
		
		status0 = StringVar()
		ttk.Label(middle, textvariable=status0, justify='center').grid(column=0, row=7)
		status1 = StringVar()
		ttk.Label(middle, textvariable=status1, justify='center').grid(column=0, row=8)
		
		root.mainloop()
		
		
	else: ## Running program without GUI##
		# Getting simulation parameters from user
		print("\nPlease enter values for simulation parameters when prompted or leave them blank for default values.")
		print("(Default values are displayed only if they exist.)")
		vehicle_info = {'route':route_file}
		
		pPref = input(conPre + " Name of the policy algorithm (default: 'Dijkstra') : ")
		pPref = 'Dijkstra' if pPref == '' else pPref
		
		if 'y' in input(conPre + ' Does this policy need any additional input arguments? [y/n] : ').lower():
			policyArgs = input(conPre + ' Please enter them in the correct order, separated by spaces : ').split()
		else:
			policyArgs = []
		
		cPref = input(conPre + " Enter the controller module name if different from policy name, else leave blank : ")
		cPref = pPref if cPref == '' else cPref
		
		vehicle_info['controlled'] = 0
		while vehicle_info['controlled'] < 1:
			vehicle_info['controlled'] = input(conPre + ' Number of vehicles controlled by the policy (min: 1, default: 10) : ')
			vehicle_info['controlled'] = 10 if vehicle_info['controlled'] == '' else int(vehicle_info['controlled'])
		
		vehicle_info['uncontrolled'] = 0
		while vehicle_info['uncontrolled'] < 1:
			vehicle_info['uncontrolled'] = input(conPre + ' Number of vehicles NOT controlled by the policy (min: 1, default: 50) : ')
			vehicle_info['uncontrolled'] = 50 if vehicle_info['uncontrolled'] == '' else int(vehicle_info['uncontrolled'])
		
		vehicle_info['pattern'] = 0
		while vehicle_info['pattern'] not in (1,2,3):
			vehicle_info['pattern'] = input(conPre + ' Start/destination pattern # [1,2,3] (default: 1) : ')
			vehicle_info['pattern'] = 1 if vehicle_info['pattern'] == '' else int(vehicle_info['pattern'])
			
		runs = 0
		while runs < 1:
			runs = input(conPre + ' Number of times to run the experiment; results will be averaged (min:1, default: 1) : ')
			runs = 1 if runs == '' else int(runs)
		print()
		
		
		## Setting up simulation ##
		print('Setting things up. . .')
		sumo_binary = checkBinary('sumo')
		
		try:
			exec("from controller." + cPref + "Controller import *")
		except Exception as err:
			print("!!! Could not load policy controller module with the given name.")
			sys.exit('Reason: ' + str(type(err))[8:-2] + ': ' + str(err) + '\n')
		
		init_connection_info = ConnectionInfo(net_file)
		print("Using network file", net_file)
		print("Using route file", route_file)
		
		try:
			scheduler = eval(pPref + "Policy(init_connection_info, *policyArgs)")
		except Exception as err:
			print("!!! Could not load policy from the given controller.")
			sys.exit('Reason: ' + str(type(err))[8:-2] + ': ' + str(err) + '\n')
		
		
		## Running simulation(s) ##
		print('\nRunning simulation(s). . .')
		try:
			print("Testing " + pPref + " Algorithm Route Controller")
			total_time, end_number, deadlines_missed = test_policy(vehicle_info, init_connection_info, sumo_binary, scheduler, runs)
		except Exception as err:
			print("!!! The following", str(type(err))[8:-2], "occurred while testing the policy:")
			raise(err)
		
		
		## Printing results ##
		print('\nSimulations complete! Results:')
		print(conPre, 'Average total simulation runtime:', total_time)
		print(conPre, 'Average vehicle roadtime:', 'N/A' if end_number == 0 else str(total_time/end_number))
		print(conPre, 'Total vehicle number:', vehicle_info['controlled'])
		print(conPre, 'Average deadlines missed:', vehicle_info['controlled'] - end_number + deadlines_missed)
		print(conPre, 'On average,', vehicle_info['controlled'] - end_number, 'vehicles could not reach their destinations.\n')