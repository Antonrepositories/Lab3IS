import random 
from algorithm import genetic_algorithm, TIMESLOTS

def print_schedule(schedule, lecturers, groups, auditoriums):
    schedule_dict = {}  
    for event in schedule.events:
        if event.timeslot not in schedule_dict:
            schedule_dict[event.timeslot] = []  
        schedule_dict[event.timeslot].append(event) 

    lecturer_hours = {lecturer_id: 0 for lecturer_id in lecturers}

    print(f"{'Timeslot':<25} {'Group(s)':<30} {'Subject':<30} {'Type':<15} "
          f"{'Lecturer':<25} {'Auditorium':<10} {'Students':<10} {'Capacity':<10}")
    print(">" * 167)

    for timeslot in TIMESLOTS:
        if timeslot in schedule_dict:
            for event in schedule_dict[timeslot]:
                group_info = ', '.join([
                    f"{gid}" + (
                        f" (Subgroup {event.subgroup_ids[gid]})" if event.subgroup_ids and gid in event.subgroup_ids else ''
                    )
                    for gid in event.group_ids
                ])
                total_students = sum(
                    groups[gid]['NumStudents'] // 2 if event.subgroup_ids and gid in event.subgroup_ids else
                    groups[gid]['NumStudents']
                    for gid in event.group_ids
                )
                auditorium_capacity = auditoriums[event.auditorium_id]

                print(f"{timeslot:<25} {group_info:<30} {event.subject_name:<30} {event.event_type:<15} "
                      f"{lecturers[event.lecturer_id]['LecturerName']:<25} {event.auditorium_id:<10} "
                      f"{total_students:<10} {auditorium_capacity:<10}")

                lecturer_hours[event.lecturer_id] += 1.5
        else:
            print(f"{timeslot:<25} {'FREE':<120}")
        print()  

    print("\nТижнева кількість годин лекторів:")
    print(f"{'Lecturer':<25} {'Total Hours':<10}")
    print("-" * 35)
    for lecturer_id, hours in lecturer_hours.items():
        lecturer_name = lecturers[lecturer_id]['LecturerName']
        print(f"{lecturer_name:<25} {hours:<10} годин")


def generate_random_groups(num_groups):
    groups = {}  
    for i in range(1, num_groups + 1):
        group_id = f"G{i}" 
        num_students = random.randint(20, 35)  
        num_subgroups = 2 
        subgroups = [f"{j}" for j in range(1, num_subgroups + 1)]  
        groups[group_id] = {
            'NumStudents': num_students, 
            'Subgroups': subgroups 
        }
    return groups  


def generate_random_subjects(groups, num_subjects_per_group):
    subjects = []  
    subject_counter = 1  
    for group_id in groups:
        for _ in range(num_subjects_per_group):
            subject_id = f"S{subject_counter}"  
            subject_name = f"Предмет {subject_counter}"  
            num_lectures = random.randint(10, 20)  
            num_practicals = random.randint(10, 20)  
            requires_subgroups = random.choice([True, False])  
            week_type = random.choice(['EVEN', 'ODD', 'Both'])  
            subjects.append({
                'SubjectID': subject_id,  
                'SubjectName': subject_name,  
                'GroupID': group_id,  
                'NumLectures': num_lectures,  
                'NumPracticals': num_practicals,  
                'RequiresSubgroups': requires_subgroups,  
                'WeekType': week_type  
            })
            subject_counter += 1 
    return subjects 


def generate_random_lecturers(num_lecturers, subjects):
    lecturers = {}  
    for i in range(1, num_lecturers + 1):
        lecturer_id = f"L{i}"  
        lecturer_name = f"Викладач {i}"  
        can_teach_subjects = random.sample(subjects, random.randint(1, min(5, len(subjects))))
        subjects_can_teach = [subj['SubjectID'] for subj in can_teach_subjects] 
        types_can_teach = random.sample(['Лекція', 'Практика'], random.randint(1, 2))
        max_hours_per_week = random.randint(20, 35) 
        lecturers[lecturer_id] = {
            'LecturerName': lecturer_name, 
            'SubjectsCanTeach': subjects_can_teach, 
            'TypesCanTeach': types_can_teach,  
            'MaxHoursPerWeek': max_hours_per_week  
        }
    return lecturers  


def generate_random_auditoriums(num_auditoriums):
    auditoriums = {}  
    for i in range(1, num_auditoriums + 1):
        auditorium_id = f"A{i}"  
        capacity = random.randint(30, 70)  
        auditoriums[auditorium_id] = capacity 
    return auditoriums  


def print_individual_schedule(schedule, lecturer_id, lecturers, groups, auditoriums, group_id, auditorium_id):
    if lecturer_id != None:
        schedule = [event for event in schedule.events if event.lecturer_id == lecturer_id]
    if group_id != None:
        schedule = [event for event in schedule.events if group_id in event.group_ids]
    if auditorium_id != None:
        schedule = [event for event in schedule.events if event.auditorium_id == auditorium_id]


    #Перевіряємо, чи є події для цього викладача
    if not schedule:
        print(f"Розклад для викладача {lecturers[lecturer_id]['LecturerName']} не знайдено.")
        return

    schedule.sort(key=lambda x: x.timeslot)

    if lecturer_id != None:
        print(f"Розклад для викладача: {lecturers[lecturer_id]['LecturerName']}")
    if group_id != None:
        print(f"Розклад для групи: {group_id}")
    if auditorium_id != None:
        print(f"Розклад для аудиторії: {auditorium_id}")
    #print(f"Розклад для викладача: {lecturers[lecturer_id]['LecturerName']}")
    print(f"{'Timeslot':<25} {'Group(s)':<30} {'Subject':<30} {'Type':<15} {'Lecturer':<10}"
          f"{'Auditorium':<10} {'Students':<10} {'Capacity':<10}")
    print("-" * 140)

    for event in schedule:
        group_info = ', '.join([
            f"{gid}" + (
                f" (Subgroup {event.subgroup_ids[gid]})" if event.subgroup_ids and gid in event.subgroup_ids else ''
            )
            for gid in event.group_ids
        ])
        
        total_students = sum(
            groups[gid]['NumStudents'] // 2 if event.subgroup_ids and gid in event.subgroup_ids else
            groups[gid]['NumStudents']
            for gid in event.group_ids
        )
        
        auditorium_capacity = auditoriums[event.auditorium_id]

        print(f"{event.timeslot:<25} {group_info:<30} {event.subject_name:<30} {event.event_type:<15} {event.lecturer_id:<10}"
              f"{event.auditorium_id:<10} {total_students:<10} {auditorium_capacity:<10}")

    print(">" * 128)
    print("End of  schedule\n")


def main():
    num_groups = 4 
    num_subjects_per_group = 3 
    num_lecturers = 6 
    num_auditoriums = 7
    groups = generate_random_groups(num_groups)
    subjects = generate_random_subjects(groups, num_subjects_per_group)
    lecturers = generate_random_lecturers(num_lecturers, subjects)
    auditoriums = generate_random_auditoriums(num_auditoriums)

    best_schedule = genetic_algorithm(groups, subjects, lecturers, auditoriums)
    print("\nBest schedule:\n")
    #print_schedule(best_schedule, lecturers, groups, auditoriums)  # Виводимо найкращий знайдений розклад
    lecturer_id = random.choice(list(lecturers.keys()))
    group_id = random.choice(list(groups.keys()))
    aud_id = random.choice(list(auditoriums.keys()))
    print_individual_schedule(best_schedule, lecturer_id, lecturers, groups, auditoriums, None, None)
    print_individual_schedule(best_schedule, None, lecturers, groups, auditoriums, group_id, None)
    print_individual_schedule(best_schedule, None, lecturers, groups, auditoriums, None, aud_id)


main()