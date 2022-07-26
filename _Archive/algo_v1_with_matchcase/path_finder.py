# TITLE: path_finder.py
# AUTHOR: Xiong Ying
# DATE: 09/07/2022 Saturday
# PURPOSE: To find the Shortest Hamiltonian Path for the ROBOT to traverse through 5 obstacles


from map import*
from trip_planner import*


# FUNCTION: calculate the ROBOT's desired location and facing angle, based on the obstacles' location and direction
# RETURN: list of tuple [()] that records all the desired vertex
def findVertex(obstacles):
    # Initialize empty list
    vertex = []
    vertex_position = ()
    # For each obstacles, calculate the desired vertex position and angle that the robot need to be
    for obstacle in obstacles:
        match obstacle[2]:
            case 0:
                vertex_position = (obstacle[0] + OBSTACLE_WIDTH + CLEARANCE, obstacle[1] - 1, 2)
                #print(vertex_position)
            case 1:
                vertex_position = (obstacle[0] - 1, obstacle[1] + OBSTACLE_WIDTH + CLEARANCE, 3)
                #print(vertex_position)
            case 2:
                vertex_position = (obstacle[0] - CLEARANCE - ROBOT_BORDER, obstacle[1] - 1, 0)
                #print(vertex_position)
            case 3:
                vertex_position = (obstacle[0] - 1, obstacle[1] - CLEARANCE - ROBOT_BORDER, 1)
                #print(vertex_position)
            case default:
                return None

        if checkAccessible(vertex_position) == True:
            vertex.append(vertex_position)
        else:
            print("WARNING: This obstacle ", obstacle, " is not accessible, please change position of it.")
            continue


    return vertex
    # End of function findVertex(obstacles)


# FUNCTION: calculate the obstacle's location and facing angle, based on the robot scanning position
# RETURN: list of tuple [()] that records all the obstacles
def findObstacles(vertices):
    # Initialize empty list
    obstacle_list = []
    obstacle = ()
    # For each obstacles, calculate the desired vertex position and angle that the robot need to be
    for vertex in vertices:
        match vertex[2]:
            case 0:
                obstacle = (vertex[0] + CLEARANCE + ROBOT_BORDER, vertex[1] + 1, 2)
            case 1:
                obstacle = (vertex[0] + 1, vertex[1] + CLEARANCE + ROBOT_BORDER, 3)
            case 2:
                obstacle = (vertex[0] - OBSTACLE_WIDTH - CLEARANCE, vertex[1] + 1, 0)
            case 3:
                obstacle = (vertex[0] + 1, vertex[1] - OBSTACLE_WIDTH - CLEARANCE, 1)
            case default:
                return None

        if checkIsObstacle(obstacle) == True:
            obstacle_list.append(obstacle)
        else:
            print("WARNING: Cannot find obstacle ", obstacle, ".")
            continue


    return obstacle_list
    # End of function findObstacles(Vertex)



# Function: find a Hamiltonian path of all Vertex using nearest neighbour greedy heuristic algorithm
# RETURN: list of tuple [()] that records all the desired vertex based on the shortest greedy distance
def findGreedyPath(node, vertex):

    # Initialize a local list to store the shortest distance from current node to each vertex
    distance = [100 for i in range (len(vertex))] # 100 is just a random super big number
    # a local variable foor distance comparison
    nearest = 100 # 100 is just a random super big number
    # a local list to store the visited flag for 5 vertex
    visited = [0 for i in range(len(vertex))]
    # record the current node position
    currentNode = node
    # empty list
    plannedPath = []

    # loop 5 times to find the sequence of 5 vertex in planned path
    for i in range(len(vertex)):
        # for each node in the planned path, compute the distance from current node
        for j in range(len(vertex)):

            if visited[j] == 0:
                # compute the distance from current node to jth node
                distance[j] = (abs(currentNode[0] - vertex[j][0])**2 + abs(currentNode[1] - vertex[j][1])**2 ) ** 0.5

        # find the node with nearest distance from current node
        nearest = min(distance)

        for k in range(len(distance)):
            if distance[k] == nearest and visited[k] == 0:
                # append the nearest node to plannedPath
                plannedPath.append(vertex[k])
                # set visited flag to 1
                visited[k] = 1
                # set kth node distance to a random big number, so it won't interfere subsequent calculation
                distance[k] = 100

    return plannedPath
    # End of function findGreedyPath(vertex, ROBOT)


# FUNCTION: compute the Hamiltonian path to traverse all vertex
# RETURN: [[()]] list of list of tuples, indicates the next nodes that the robot will go
def planPath(obstacles_from_app):

    ''' 1.  Mark obstacles coordinate on the MAP '''

    # NEW
    # remove the id from obstacle_from_app

    # OBSTACLE FORMAT:
    # tuple = (x coordinate, y coordinate, direction)
    # a tuple with the position of the obstacle and image facing direction

    # x coordinate = x coordinate of the bottom left corner of obstacle
    # y coordinate = y coordinate of the bottom left corner of obstacle
    # direction = { 0:East, 1:North, 2:West, 3:South }

    #obstacles = [(5, 7, 3), (5, 13, 2), (12, 9, 0), (15, 4, 1), (15, 15, 3)]

    obstacles = []
    for i in range(len(obstacles_from_app)):
        obstacles.append(obstacles_from_app[i][1:])

    print(obstacles)


    # 1 = obstacle / non-accessible, 0 = empty / accesible
    markObstaclesOnMAP(obstacles)
    # Print the MAP
    printMap()

    # Helper function
    markAccessOnMAP(obstacles)
    #printAccessMap()


    ''' 2.  Find all desired location and direction in order to scan 5 images '''

    vertex = findVertex(obstacles)
    # print
    print("Robot will go to", len(vertex), "vertex: ", vertex)
    print(" ")


    ''' 3. Path finding: plan a Hamiltonian Path to access all vertex '''

    # only use greedy heuristic algorithm to plan the path
    path = findGreedyPath(ROBOT_POSITION,vertex)
    # print
    print("Found a greedy Hamiltonian Path: ", path)
    print(" ")

    # NEW
    # Find the corresbonding OBSTACLES id
    obstacles_seq = findObstacles(path)
    obstacles_id = []
    for obstacle in obstacles_seq:
        for obstacle_with_id in obstacles_from_app:
            if obstacle[0] == obstacle_with_id[1] and obstacle[1] == obstacle_with_id[2] and obstacle[2] == obstacle_with_id[3]:
                obstacles_id.append(obstacle_with_id[0])
    print("The obstacles id sequence: ", obstacles_id)
    print(" ")



    ''' 4. for each section of the path, find the shortest trip between 2 Vertex '''

    # add robot's initial position to in front of the path
    path = [ROBOT_POSITION] + path

    # initialize empty trip list and cost
    trip_list = []
    trip_cost = 0

    # traverse the greedy path until the second last vertex
    for i in range(len(path)):
        if i < len(path)-1:
            # find a trip between this vertex and the next vertex
            trip, total_cost = astar(MAP, path[i], path[i+1])

            # add the trip to trip list, add the cost of this trip to total_cost
            trip_list.append(trip)
            trip_cost += total_cost

    # print out the shortest trip
    print("The shorter trip:")
    for single_trip in trip_list:
        print(single_trip)
    print(" ")

    # print out the total cost of the path
    #print("Total cost of this path :", trip_cost)


    ''' 5. convert the planned trip to instructions '''
    # Instructions: move_forward, move_backward, turn_left, turn_right
    instruction = convertInstruction(trip_list)

    # print out the instructions
    print("The instruction to move:")
    for one_instruction in instruction:
        print(one_instruction, ",")

    # return the instructions
    return instruction, obstacles_seq


# FUNCTION: convert a list of node to movement instructions
# RETURN: list of list
# direction = {"fwd":"forward", "rev":"reverse", "tl":"turn left", "tr":"turn right"}
def convertInstruction(trip_list):
    # initialize an empty list of list [[]]
    instruction = [[] for i in range(len(trip_list))]

    # traverse each trip in trip list

    for i in range(len(trip_list)):
        #print("outer for loop ",i, ": ",trip_list[i])

        # traverse from the first element to the second last element
        for j in range(len(trip_list[i])-1):
            #print("inner for loop ",j, ": ",trip_list[i][j])
            # print(single_trip, ": ", i," th element")

            start_x = trip_list[i][j][0]
            start_y = trip_list[i][j][1]
            start_direction = trip_list[i][j][2]
            #print("start_direction : ", start_direction)

            end_x = trip_list[i][j+1][0]
            end_y = trip_list[i][j+1][1]
            end_direction = trip_list[i][j+1][2]
            #print("end_direction : ", end_direction)
            #print("")

            if end_direction == start_direction: # direction is the same
                # differentiate forward or backward
                match start_direction:
                    # east
                    case 0:
                        if end_x > start_x:
                            move = "fwd"
                        elif end_x < start_x:
                            move = "rev"
                        else:
                            move = "error"
                    # north
                    case 1:
                        if end_y > start_y:
                            move = "fwd"
                        elif end_y < start_y:
                            move = "rev"
                        else:
                            move = "error"
                    # west
                    case 2:
                        if end_x < start_x:
                            move = "fwd"
                        elif end_x > start_x:
                            move = "rev"
                        else:
                            move = "error"
                    # south
                    case 3:
                        if end_y < start_y:
                            move = "fwd"
                        elif end_y > start_y:
                            move = "rev"
                        else:
                            move = "error"
                    case default:
                        move = "error"
            elif (end_direction - start_direction)%4 == 1: # turn left
                move = "tl"
            elif (end_direction - start_direction)%4 == 3: # turn right, +3 is the same as -1
                move = "tr"
            else:
                move = "error"

            instruction[i].append(move)
            #print("instruction is ", instruction)

    return instruction
    # End of function convertInstruction(trip_list)


# FUNCTION: compute permutation for the path
def permutations(orig_list):
    if not isinstance(orig_list, list):
        orig_list = list(orig_list)

    yield orig_list

    if len(orig_list) == 1:
        return

    for n in sorted(orig_list):
        new_list = orig_list[:]
        pos = new_list.index(n)
        del(new_list[pos])
        new_list.insert(0, n)
        for resto in permutations(new_list[1:]):
            if new_list[:1] + resto != orig_list:
                yield new_list[:1] + resto
    # End of Function permutations (orig_list)


# FUNCTION: compute the shortest Hamiltonian path to traverse all vertex, with permutation
# RETURN: [[()]] list of list of tuples, indicates the next nodes that the robot will go
# BE CAUTIOUS when using this function, computational time will be exponential
def planShortestPath(obstacles_from_app):



    ''' 1.  Mark obstacles coordinate on the MAP '''

    # NEW
    # remove the id from obstacle_from_app

    # OBSTACLE FORMAT:
    # tuple = (x coordinate, y coordinate, direction)
    # a tuple with the position of the obstacle and image facing direction

    # x coordinate = x coordinate of the bottom left corner of obstacle
    # y coordinate = y coordinate of the bottom left corner of obstacle
    # direction = { 0:East, 1:North, 2:West, 3:South }

    #obstacles = [(5, 7, 3), (5, 13, 2), (12, 9, 0), (15, 4, 1), (15, 15, 3)]

    obstacles = []
    for i in range(len(obstacles_from_app)):
        obstacles.append(obstacles_from_app[i][1:])

    print(obstacles)



    # 1 = obstacle / non-accessible, 0 = empty / accesible
    markObstaclesOnMAP(obstacles)
    # Print the MAP
    printMap()

    # Helper function
    markAccessOnMAP(obstacles)
    #printAccessMap()


    ''' 2.  Find all desired location and direction in order to scan 5 images '''

    vertex = findVertex(obstacles)
    # print
    print("Robot will go to", len(vertex), "vertex: ", vertex)
    print(" ")


    ''' 3. Path finding: plan a Hamiltonian Path to access all vertex '''

    # only use greedy heuristic algorithm to plan the path
    greedyPath = findGreedyPath(ROBOT_POSITION,vertex)
    # print
    print("Found a Hamiltonian Path: ", greedyPath)
    print(" ")
    #path2 = greedyPath[0::2]
    #allPaths = [greedyPath, path2]
    allPaths = permutations(greedyPath) ############################
    print("generatinig permutations for all vertex:")


    ''' 4. for each section of the path, find the shortest trip between 2 Vertex '''

    shortestTrip = []
    smallestCost = 9999
    shortestPath = []

    for path in allPaths:
        print("path = ", path)
        # add robot's initial position to in front of the path
        path = [ROBOT_POSITION] + path
        trip_list = []
        trip_cost = 0
        for i in range(len(path)):
            if i < len(path)-1:
                trip, total_cost = astar(MAP, path[i], path[i+1])
                trip_list.append(trip)
                trip_cost += total_cost

        # print
        print("trip_list = ", trip_list)
        print("trip_cost = ", trip_cost)
        print("")

        if trip_cost < smallestCost:
            #print("It's shorter!!!")
            shortestTrip = trip_list
            #print("The shortest path is ", shortestTrip)
            smallestCost = trip_cost
            #print("The smallestCost is ", smallestCost)
            shortestPath = path[1:]
            print("The shortestPath is ", shortestPath)


    # NEW
    # Find the corresbonding OBSTACLES id
    obstacles_seq = findObstacles(shortestPath)
    obstacles_id = []
    for obstacle in obstacles_seq:
        for obstacle_with_id in obstacles_from_app:
            if obstacle[0] == obstacle_with_id[1] and obstacle[1] == obstacle_with_id[2] and obstacle[2] == obstacle_with_id[3]:
                obstacles_id.append(obstacle_with_id[0])
    print("The obstacles id sequence: ", obstacles_id)
    print(" ")


    # print out the shortest trip
    print("The shortest trip:")
    for single_trip in shortestTrip:
        print(single_trip)

    # print out the total cost of the path
    print(" ")
    print("Total cost of the shortest trip:", smallestCost)



    ''' 5. convert the planned trip to instructions '''
    # Instructions: move_forward, move_backward, turn_left, turn_right
    instruction = convertInstruction(shortestTrip)


    # print out the instructions
    print(" ")
    print("The instruction to move:")
    for one_instruction in instruction:
        print(one_instruction, ",")

    # return the instructions

    return instruction, obstacles_id


# Sample obstacles position for testing function planPath()
def main():
    print("path_finder.py")

    # Get info from other modules

    

    # Sample obstacles for testing

    # get obstacles from app

    # obstacles_from_app FORMAT:
    # tuple = (obstacle_id, x coordinate, y coordinate, direction)
    # a tuple with the id, the position of the obstacle and image facing direction

    # obstacle_id = the id assigned to the obstacle by the app
    # x coordinate = x coordinate of the bottom left corner of obstacle
    # y coordinate = y coordinate of the bottom left corner of obstacle
    # direction = { 0:East, 1:North, 2:West, 3:South }

    obstacles_from_app = [(1, 5, 7, 3), (2, 5, 13, 2), (3, 12, 9, 0), (4, 15, 4, 1), (5, 15, 15, 3)]
    # will get obstacles = [(5, 7, 3), (5, 13, 0), (12, 9, 0), (5, 13, 2), (15, 15, 3)]

    # Be Cautious! If on permutation, computational time might explode

    permutation = True # By default, set to False

    # invoke path finder
    # return: list of list

    if permutation == True:
        movement, obstacles_id = planShortestPath(obstacles_from_app)
    else:
        movement, obstacles_id = planPath(obstacles_from_app)




if __name__ == "__main__":
    main()
