from controller.RouteController import RouteController
from core.Util import ConnectionInfo, Vehicle
import sumolib
from sumolib import net
import traci
import math



class AstarPolicy(RouteController):
	def __init__(self, connection_info):
		self.net = sumolib.net.readNet(connection_info.net_filename)
		super().__init__(connection_info)

	def make_decisions(self, vehicles, connection_info):
		"""
		Uses the A* algorithm to find the shortest path to the destination for each vehicle
		
		Code is based on pseudocode from https://en.wikipedia.org/wiki/A*_search_algorithm#Pseudocode

		:param vehicles: list of vehicles to make routing decisions for
		:param connection_info: object containing network information
		:return: local_targets: {vehicle_id, target_edge}, where target_edge is a local target to send to TRACI
		"""

		local_targets = {}
		for vehicle in vehicles:
			start_edge = vehicle.current_edge

			'''  Your algo starts here '''
			decision_list = []
			
			openSet = [start_edge]
			cameFrom = {}
			
			gScore = {}
			fScore = {}
			for edge in connection_info.edge_list:
				gScore[edge] = float('inf')
				fScore[edge] = float('inf')
			gScore[start_edge] = 0
			fScore[start_edge] = self.h(vehicle, start_edge)
			
			while len(openSet) > 0:
				temp = float('inf')
				for edge in openSet:
					if fScore[edge] < temp:
						temp = fScore[edge]
						current = edge
				openSet.pop(openSet.index(current))
				
				if current == vehicle.destination:
					total_path = [current]
					while current in cameFrom.keys():
						current = cameFrom[current]
						total_path.insert(0, current)
					
					for i in range(len(total_path)-1):
						next = total_path[i+1]
						for d, e in connection_info.outgoing_edges_dict[total_path[i]].items():
							if e == next:
								decision_list.append(d)
								break
					break
				
				for dir, edge in connection_info.outgoing_edges_dict[current].items():
					tentative_gScore = gScore[current] + connection_info.edge_length_dict[edge]
					if tentative_gScore < gScore[edge]:
						cameFrom[edge] = current
						gScore[edge] = tentative_gScore
						fScore[edge] = tentative_gScore + self.h(vehicle, edge)
						if edge not in openSet:
							openSet.append(edge)
			
			
			local_targets[vehicle.vehicle_id] = self.compute_local_target(decision_list, vehicle)

		return local_targets
	
	def h(self, vehicle, start_edge):
		'''
			This is the heuristic function used by the A* algorithm.
			In this implementation, the heuristic is the euclidean distance
				between the midpoints of start_edge and vehicle.destination.
		'''
		
		points = self.net.getEdge(start_edge).getShape()
		startpoint = ((points[0][0] + points[1][0])/2, ((points[0][1] + points[1][1])/2))
		
		points = self.net.getEdge(start_edge).getShape()
		destpoint = ((points[0][0] + points[1][0])/2, ((points[0][1] + points[1][1])/2))
		
		return math.sqrt((destpoint[0] - startpoint[0])**2 + (destpoint[1] - startpoint[1])**2)