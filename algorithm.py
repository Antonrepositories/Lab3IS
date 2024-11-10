import random
import copy
import math


DAYS_PER_WEEK = 5

LESSONS_PER_DAY = 4

WEEK_TYPE = ['EVEN', 'ODD']

TOTAL_LESSONS = DAYS_PER_WEEK * LESSONS_PER_DAY * len(WEEK_TYPE)

TIMESLOTS = [f"{week} - day {day + 1}, lesson {slot + 1}"
             for week in WEEK_TYPE
             for day in range(DAYS_PER_WEEK)
             for slot in range(LESSONS_PER_DAY)]


class Event:
    def __init__(self, timeslot, group_ids, subject_id, subject_name, lecturer_id, auditorium_id, event_type,
                 subgroup_ids=None, week_type='Both'):
        self.timeslot = timeslot
        self.group_ids = group_ids  
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.lecturer_id = lecturer_id
        self.auditorium_id = auditorium_id
        self.event_type = event_type  
        self.subgroup_ids = subgroup_ids  
        self.week_type = week_type


class Schedule:
    def __init__(self):
        self.events = []
        self.soft_constraints_score = 0 
        self.hard_consts_score = 0

    def add_event(self, event):
        if event:
            self.events.append(event)  

    def fitness(self, groups, lecturers, auditoriums, subjects):
        hard_constraints_violations = 0 
        soft_constraints_score = 0  
        lecturer_times = {}
        group_times = {}
        subgroup_times = {}
        auditorium_times = {}
        lecturer_hours = {}
        subject_hours = {}

        for event in self.events:
            #Hard обмеження
            lecturert_key = (event.lecturer_id, event.timeslot)
            if lecturert_key in lecturer_times:
                #hard_constraints_violations += 1  
                if lecturer_times[lecturert_key] != event:
                    hard_constraints_violations += 1  
                    #print(hard_constraints_violations)
            else:
                lecturer_times[lecturert_key] = event
            for group_id in event.group_ids:
                group_key = (group_id, event.timeslot)
                if group_key in group_times:
                    #hard_constraints_violations += 1  
                    if group_times[group_key] != event:
                        hard_constraints_violations += 1  
                        #print(hard_constraints_violations)
                else:
                    group_times[group_key] = event
                if event.subgroup_ids and group_id in event.subgroup_ids:
                    subgroup_id = event.subgroup_ids[group_id]
                    sgt_key = (group_id, subgroup_id, event.timeslot)
                    if sgt_key in subgroup_times:
                        #hard_constraints_violations += 1  
                        if subgroup_times[sgt_key] != event:
                            hard_constraints_violations += 1  
                            #print(hard_constraints_violations)
                    else:
                        subgroup_times[sgt_key] = event

            at_key = (event.auditorium_id, event.timeslot)
            if at_key in auditorium_times:
                existing_event = auditorium_times[at_key]
                if (event.event_type == 'Лекція' and existing_event.event_type == 'Лекція' and event.lecturer_id == existing_event.lecturer_id):# and len(same_lecturer_events) == 1):
                    #Об'єднуємо лекції з одним викладачем
                    pass
                else:
                    hard_constraints_violations += 1  
            else:
                auditorium_times[at_key] = event

            #Soft обмеження
            week = event.timeslot.split(' - ')[0]
            lecturer_hours_key = (event.lecturer_id, week)
            lecturer_hours[lecturer_hours_key] = lecturer_hours.get(lecturer_hours_key, 0) + 1.5
            if lecturer_hours[lecturer_hours_key] > lecturers[event.lecturer_id]['MaxHoursPerWeek']:
                #print(f"Lecturer hours {lecturer_hours[lecturer_hours_key]} {event.lecturer_id}")
                soft_constraints_score += 1
                  
            subject_hours_key = (event.subject_id)
            subject_hours[subject_hours_key] = subject_hours.get(subject_hours_key, 0) + 1.5
            total_group_size = sum(
                groups[g]['NumStudents'] // 2 if event.subgroup_ids and event.subgroup_ids.get(g) else groups[g][
                    'NumStudents']
                for g in event.group_ids)
            if auditoriums[event.auditorium_id] < total_group_size:
                soft_constraints_score += 1  

            if event.subject_id not in lecturers[event.lecturer_id]['SubjectsCanTeach']:
                soft_constraints_score += 1  
            if event.event_type not in lecturers[event.lecturer_id]['TypesCanTeach']:
                soft_constraints_score += 1
            
        for subject in subjects:
            subject_id = subject['SubjectID']
            subject_num_lessons = (subject['NumLectures'] + subject['NumPracticals']) * 1.5 
            if subject_id in subject_hours:
                if subject_hours[subject_id] > subject_num_lessons:
                    soft_constraints_score += subject_hours[subject_id] - subject_num_lessons
                else:
                    soft_constraints_score += subject_num_lessons - subject_hours[subject_id]
            else:
                soft_constraints_score += subject_num_lessons
        total_score = hard_constraints_violations * 10 + soft_constraints_score  
        self.soft_constraints_score = soft_constraints_score 
        self.hard_consts_score = hard_constraints_violations
        return total_score


def generate_initial_population(pop_size, groups, subjects, lecturers, auditoriums):
    population = []
    for _ in range(pop_size):
        lecturer_times = {} 
        group_times = {}  
        subgroup_times = {} 
        auditorium_times = {}  
        schedule = Schedule()

        for subj in subjects:
            weeks = [subj['WeekType']] if subj['WeekType'] in WEEK_TYPE else WEEK_TYPE
            for week in weeks:
                for _ in range(subj['NumLectures']):
                    event = create_random_event(
                        subj, groups, lecturers, auditoriums, 'Лекція', week,
                        lecturer_times, group_times, subgroup_times, auditorium_times
                    )
                    if event:
                        schedule.add_event(event)
                        lecturer_times.update({(event.lecturer_id, event.timeslot) : event})
                        auditorium_times.update({(event.auditorium_id, event.timeslot): event})
                        for g in event.group_ids:
                                    group_times.update({(g, event.timeslot) : event})

                for _ in range(subj['NumPracticals']):
                    if subj['RequiresSubgroups']:
                        #Для кожної підгрупи створюємо окрему подію
                        for subgroup_id in groups[subj['GroupID']]['Subgroups']:
                            subgroup_ids = {subj['GroupID']: subgroup_id}
                            event = create_random_event(
                                subj, groups, lecturers, auditoriums, 'Практика', week,
                                lecturer_times, group_times, subgroup_times, auditorium_times, subgroup_ids
                            )
                            if event:
                                schedule.add_event(event)
                                lecturer_times.update({(event.lecturer_id, event.timeslot) : event})
                                auditorium_times.update({(event.auditorium_id, event.timeslot): event})
                                for g in event.group_ids:
                                    group_times.update({(g, event.timeslot) : event})
                                    if g in event.subgroup_ids:
                                        for subgroup_id in event.subgroup_ids[g]:
                                            subgroup_key = (g, subgroup_id, event.timeslot)
                                            subgroup_times.update({subgroup_key : event})
                                
                    else:
                        event = create_random_event(
                            subj, groups, lecturers, auditoriums, 'Практика', week,
                            lecturer_times, group_times, subgroup_times, auditorium_times
                        )
                        if event:
                            schedule.add_event(event)
                            lecturer_times.update({(event.lecturer_id, event.timeslot) : event})
                            auditorium_times.update({(event.auditorium_id, event.timeslot): event})
                            for g in event.group_ids:
                                    group_times.update({(g, event.timeslot) : event})
                                

        population.append(schedule)

    return population


def create_random_event(subj, groups, lecturers, auditoriums, event_type, week_type, lecturer_times, group_times, subgroup_times, auditorium_times, subgroup_ids=None):
    global lecturer_key
    timeslot = random.choice([t for t in TIMESLOTS if t.startswith(week_type)])

    suitable_lecturers = [
        lid for lid, l in lecturers.items()
        if subj['SubjectID'] in l['SubjectsCanTeach'] and event_type in l['TypesCanTeach']
    ]
    if not suitable_lecturers:
        return None  

    random.shuffle(suitable_lecturers)
    lecturer_id = None
    for lid in suitable_lecturers:
        lecturer_key = (lid, timeslot)
        if lecturer_key not in lecturer_times:
            lecturer_id = lid
            break
    if not lecturer_id:
        return None 

    if event_type == 'Лекція':
        available_groups = [gid for gid in groups if (gid, timeslot) not in group_times]
        if not available_groups:
            return None
        num_groups = random.randint(1, min(3, len(available_groups)))
        group_ids = random.sample(available_groups, num_groups)
    else:
        group_ids = [subj['GroupID']]
        if (group_ids[0], timeslot) in group_times:
            return None

    for group_id in group_ids:
        group_key = (group_id, timeslot)
        if group_key in group_times:
            return None 

    if event_type == 'Практика' and subj['RequiresSubgroups']:
        available_groups = [gid for gid in groups if (gid, timeslot) not in group_times]
        if not available_groups:
            return None
        if subgroup_ids is None:
            subgroup_ids = {}
            for group_id in group_ids:
                subgroup_ids[group_id] = random.choice(groups[group_id]['Subgroups'])
        for group_id, subgroup_id in subgroup_ids.items():
            subgroup_key = (group_id, subgroup_id, timeslot)
            if subgroup_key in subgroup_times:
                return None  
    else:
        subgroup_ids = None 

    total_group_size = sum(
        groups[g]['NumStudents'] // 2 if subgroup_ids and g in subgroup_ids else groups[g]['NumStudents']
        for g in group_ids
    )
    suitable_auditoriums = [
        (aid, cap) for aid, cap in auditoriums.items() #if cap >= total_group_size
    ]
    if not suitable_auditoriums:
        return None 

    random.shuffle(suitable_auditoriums)
    auditorium_id = None
    for aid, cap in suitable_auditoriums:
        auditorium_key = (aid, timeslot)
        if auditorium_key not in auditorium_times:
            auditorium_id = aid
            break
    if not auditorium_id:
        return None

    event = Event(
        timeslot, group_ids, subj['SubjectID'], subj['SubjectName'],
        lecturer_id, auditorium_id, event_type, subgroup_ids, week_type
    )

    lecturer_times[lecturer_key] = event
    for group_id in group_ids:
        group_key = (group_id, timeslot)
        group_times[group_key] = event
        if event_type == 'Практика' and subgroup_ids and group_id in subgroup_ids:
            subgroup_id = subgroup_ids[group_id]
            subgroup_key = (group_id, subgroup_id, timeslot)
            subgroup_times[subgroup_key] = event
    auditorium_times[(auditorium_id, timeslot)] = event

    return event


def select_population(population, groups, lecturers, auditoriums, subjects, fitness_function):
    population.sort(
        key=lambda x: fitness_function(x, groups, lecturers, auditoriums, subjects))  
    return population[:len(population) // 2] if len(population) > 1 else population 

def half_best(population, groups, lecturers, auditoriums, subjects, fitness_function):
    population = select_population(population, groups, lecturers, auditoriums, subjects, fitness_function)
    return population


def rain(population_size, groups, subjects, lecturers, auditoriums):
    new_population = generate_initial_population(population_size, groups, subjects, lecturers, auditoriums)
    return new_population


def mutate(schedule, lecturers, auditoriums, intensity=0.1):
    num_events_to_mutate = int(len(schedule.events) * intensity)
    if num_events_to_mutate < 2:
        num_events_to_mutate = 2
    if num_events_to_mutate % 2 != 0:
        num_events_to_mutate += 1
    if num_events_to_mutate > len(schedule.events):
        num_events_to_mutate = len(schedule.events) - (len(schedule.events) % 2)

    events_to_mutate = random.sample(schedule.events, num_events_to_mutate)
    for i in range(0, len(events_to_mutate), 2):
        event1 = events_to_mutate[i]
        event2 = events_to_mutate[i + 1]

        if can_swap_events(event1, event2):
            event1.timeslot, event2.timeslot = event2.timeslot, event1.timeslot

            # if random.random() < 0.5 and can_swap_auditoriums(event1, event2):
            #     event1.auditorium_id, event2.auditorium_id = event2.auditorium_id, event1.auditorium_id

            # if random.random() < 0.5 and can_swap_lecturers(event1, event2):
            #     event1.lecturer_id, event2.lecturer_id = event2.lecturer_id, event1.lecturer_id
            # З випадковою ймовірністю обмінюємо аудиторії, тільки якщо це дозволено
            if can_swap_auditoriums(event1, event2):
                event1.auditorium_id, event2.auditorium_id = event2.auditorium_id, event1.auditorium_id

            # З випадковою ймовірністю обмінюємо викладачів, тільки якщо це дозволено
            if can_swap_lecturers(event1, event2):
                event1.lecturer_id, event2.lecturer_id = event2.lecturer_id, event1.lecturer_id


def can_swap_events(event1, event2):
    #Заборона, якщо одна група матиме лекцію і практику одночасно
    group_conflict = any(
        g in event2.group_ids for g in event1.group_ids) and event1.event_type != event2.event_type
    return not group_conflict


def can_swap_auditoriums(event1, event2):
    return event1.auditorium_id != event2.auditorium_id


def can_swap_lecturers(event1, event2):
    return event1.lecturer_id != event2.lecturer_id


def crossover(parent1, parent2):
    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
    crossover_point = random.randint(0, len(parent1.events) - 1)
    
    child1.events[crossover_point:], child2.events[crossover_point:] = parent2.events[crossover_point:], parent1.events[
                                                                                                         crossover_point:]
    return child1, child2


def genetic_algorithm(groups, subjects, lecturers, auditoriums, generations=35):
    global best_schedule
    population_size = 100  
    population = generate_initial_population(population_size, groups, subjects, lecturers, auditoriums)
    fitness_function = Schedule.fitness  
    ft = 100
    i = 1
    last_20_results = []
    while ft > 1 and i < generations:
        population = half_best(population, groups, lecturers, auditoriums, subjects, fitness_function)
        if not population:
            print("Population is empty")
            break
        best_schedule = population[0]
        best_fitness = fitness_function(best_schedule, groups, lecturers, auditoriums, subjects)
        print(f"Generation: {i + 1}, Best fitness: {best_fitness} Hard violations: {best_schedule.hard_consts_score}")
        i += 1
        ft = best_fitness
        if best_fitness < 1 and best_schedule.hard_consts_score == 0:
            break

        last_20_results.append(best_fitness)

        # if len(last_20_results) == 20:
        #     first_half = last_20_results[:10]
        #     second_half = last_20_results[10:]
        #     first_half_avg = sum(first_half) / len(first_half)
        #     second_half_avg = sum(second_half) / len(second_half)
        #     if second_half_avg > first_half_avg and best_schedule.hard_consts_score == 0:
        #         print("Average fitness of last 10 is higher than 10 before, no need to continue!")
        #         break
        #     else:
        #         last_20_results.clear()

        new_population = []

        rain_population = rain(len(population), groups, subjects, lecturers, auditoriums)

        new_population.extend(population)
        new_population.extend(rain_population)
        
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population, 2)
            child1, child2 = crossover(parent1, parent2)
            child1f = fitness_function(child1, groups, lecturers, auditoriums, subjects)
            child2f = fitness_function(child2, groups, lecturers, auditoriums, subjects)
            if child1.hard_consts_score == 0 and child2.hard_consts_score == 0:
                new_population.extend([child1, child2])
        
        random.shuffle(new_population)
        for schedule in new_population:
            if random.random() < 0.3:
                mutate(schedule, lecturers, auditoriums)

        population = new_population

    return best_schedule