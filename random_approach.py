import random  # Імпортуємо модуль random для генерації випадкових чисел
from algorithm import genetic_algorithm, TIMESLOTS



def print_schedule(schedule, lecturers, groups, auditoriums):
    schedule_dict = {}  # Створюємо словник для зберігання подій за часовими слотами
    for event in schedule.events:
        if event.timeslot not in schedule_dict:
            schedule_dict[event.timeslot] = []  # Ініціалізуємо список подій для нового часовго слота
        schedule_dict[event.timeslot].append(event)  # Додаємо подію до відповідного часовго слота

    # Словник для підрахунку годин викладачів
    lecturer_hours = {lecturer_id: 0 for lecturer_id in lecturers}

    # Виведення заголовків колонок
    print(f"{'Timeslot':<25} {'Group(s)':<30} {'Subject':<30} {'Type':<15} "
          f"{'Lecturer':<25} {'Auditorium':<10} {'Students':<10} {'Capacity':<10}")
    print("-" * 167)

    for timeslot in TIMESLOTS:
        if timeslot in schedule_dict:
            for event in schedule_dict[timeslot]:
                # Формуємо інформацію про групи, включаючи підгрупи, якщо вони є
                group_info = ', '.join([
                    f"{gid}" + (
                        f" (Subgroup {event.subgroup_ids[gid]})" if event.subgroup_ids and gid in event.subgroup_ids else ''
                    )
                    for gid in event.group_ids
                ])
                # Обчислюємо кількість студентів у події
                total_students = sum(
                    groups[gid]['NumStudents'] // 2 if event.subgroup_ids and gid in event.subgroup_ids else
                    groups[gid]['NumStudents']
                    for gid in event.group_ids
                )
                # Отримуємо місткість аудиторії
                auditorium_capacity = auditoriums[event.auditorium_id]

                # Виводимо інформацію по колонках
                print(f"{timeslot:<25} {group_info:<30} {event.subject_name:<30} {event.event_type:<15} "
                      f"{lecturers[event.lecturer_id]['LecturerName']:<25} {event.auditorium_id:<10} "
                      f"{total_students:<10} {auditorium_capacity:<10}")

                # Додаємо 1.5 години до загальної кількості годин викладача
                lecturer_hours[event.lecturer_id] += 1.5
        else:
            # Якщо у цьому часовому слоті немає подій, виводимо "EMPTY" у першій колонці
            print(f"{timeslot:<25} {'EMPTY':<120}")
        print()  # Додаємо порожній рядок для відділення часових слотів

    # Виводимо кількість годин викладачів на тиждень
    print("\nКількість годин лекторів на тиждень:")
    print(f"{'Lecturer':<25} {'Total Hours':<10}")
    print("-" * 35)
    for lecturer_id, hours in lecturer_hours.items():
        lecturer_name = lecturers[lecturer_id]['LecturerName']
        print(f"{lecturer_name:<25} {hours:<10} годин")


# Функції для випадкової генерації даних
def generate_random_groups(num_groups):
    groups = {}  # Створюємо порожній словник для груп
    for i in range(1, num_groups + 1):
        group_id = f"G{i}"  # Створюємо ідентифікатор групи (наприклад, 'G1')
        num_students = random.randint(20, 35)  # Випадкова кількість студентів у групі від 20 до 35
        # Генеруємо підгрупи: мінімум 2 підгрупи для кожної групи
        num_subgroups = 2  # Створюємо 2 підгрупи (можна змінити на рандомну кількість)
        subgroups = [f"{j}" for j in range(1, num_subgroups + 1)]  # Наприклад, ['1', '2']
        groups[group_id] = {
            'NumStudents': num_students,  # Кількість студентів
            'Subgroups': subgroups  # Список підгруп
        }
    return groups  # Повертаємо словник з групами


# Функція для генерації випадкових предметів для кожної групи
def generate_random_subjects(groups, num_subjects_per_group):
    subjects = []  # Створюємо порожній список для предметів
    subject_counter = 1  # Лічильник для унікальних ідентифікаторів предметів
    for group_id in groups:
        for _ in range(num_subjects_per_group):
            subject_id = f"S{subject_counter}"  # Створюємо ідентифікатор предмета (наприклад, 'S1')
            subject_name = f"Предмет {subject_counter}"  # Назва предмета
            num_lectures = random.randint(10, 20)  # Випадкова кількість лекцій від 10 до 20
            num_practicals = random.randint(10, 20)  # Випадкова кількість практичних занять від 10 до 20
            requires_subgroups = random.choice([True, False])  # Випадково визначаємо, чи потрібні підгрупи
            week_type = random.choice(['EVEN', 'ODD', 'Both'])  # Випадково вибираємо тип тижня
            subjects.append({
                'SubjectID': subject_id,  # Ідентифікатор предмета
                'SubjectName': subject_name,  # Назва предмета
                'GroupID': group_id,  # Група, для якої призначений предмет
                'NumLectures': num_lectures,  # Кількість лекцій
                'NumPracticals': num_practicals,  # Кількість практичних занять
                'RequiresSubgroups': requires_subgroups,  # Чи потрібен поділ на підгрупи
                'WeekType': week_type  # Тип тижня: 'EVEN', 'ODD' або 'Both'
            })
            subject_counter += 1  # Збільшуємо лічильник предметів
    return subjects  # Повертаємо список предметів


# Функція для генерації випадкових викладачів
def generate_random_lecturers(num_lecturers, subjects):
    lecturers = {}  # Створюємо порожній словник для викладачів
    for i in range(1, num_lecturers + 1):
        lecturer_id = f"L{i}"  # Створюємо ідентифікатор викладача (наприклад, 'L1')
        lecturer_name = f"Викладач {i}"  # Ім'я викладача
        # Випадково вибираємо предмети, які викладач може викладати (від 1 до 5 предметів)
        can_teach_subjects = random.sample(subjects, random.randint(1, min(5, len(subjects))))
        subjects_can_teach = [subj['SubjectID'] for subj in can_teach_subjects]  # Отримуємо ідентифікатори цих предметів
        # Випадково вибираємо типи занять, які викладач може проводити ('Лекція', 'Практика' або обидва)
        types_can_teach = random.sample(['Лекція', 'Практика'], random.randint(1, 2))
        max_hours_per_week = random.randint(10, 20)  # Випадкова максимальна кількість годин на тиждень
        lecturers[lecturer_id] = {
            'LecturerName': lecturer_name,  # Ім'я викладача
            'SubjectsCanTeach': subjects_can_teach,  # Список предметів, які може викладати
            'TypesCanTeach': types_can_teach,  # Типи занять, які може проводити
            'MaxHoursPerWeek': max_hours_per_week  # Максимальна кількість годин на тиждень
        }
    return lecturers  # Повертаємо словник викладачів


# Функція для генерації випадкових аудиторій
def generate_random_auditoriums(num_auditoriums):
    auditoriums = {}  # Створюємо порожній словник для аудиторій
    for i in range(1, num_auditoriums + 1):
        auditorium_id = f"A{i}"  # Створюємо ідентифікатор аудиторії (наприклад, 'A1')
        capacity = random.randint(30, 50)  # Випадкова місткість аудиторії від 30 до 50
        auditoriums[auditorium_id] = capacity  # Зберігаємо місткість аудиторії
    return auditoriums  # Повертаємо словник аудиторій


def print_individual_schedule(schedule, lecturer_id, lecturers, groups, auditoriums, group_id, auditorium_id):
    # Створюємо словник для зберігання подій за часовими слотами для заданого викладача
    if lecturer_id != None:
        schedule = [event for event in schedule.events if event.lecturer_id == lecturer_id]
    if group_id != None:
        schedule = [event for event in schedule.events if group_id in event.group_ids]
    if auditorium_id != None:
        schedule = [event for event in schedule.events if event.auditorium_id == auditorium_id]


    # Перевіряємо, чи є події для цього викладача
    if not schedule:
        print(f"Розклад для викладача {lecturers[lecturer_id]['LecturerName']} не знайдено.")
        return

    # Сортуємо події за часовими слотами
    schedule.sort(key=lambda x: x.timeslot)

    # Виведення заголовків колонок
    if lecturer_id != None:
        print(f"Розклад для викладача: {lecturers[lecturer_id]['LecturerName']}")
    if group_id != None:
        print(f"Розклад для групи: {group_id}")
    if auditorium_id != None:
        print(f"Розклад для аудиторії: {auditorium_id}")
    #print(f"Розклад для викладача: {lecturers[lecturer_id]['LecturerName']}")
    print(f"{'Timeslot':<25} {'Group(s)':<30} {'Subject':<30} {'Type':<15} {'Lecturer':<10}"
          f"{'Auditorium':<10} {'Students':<10} {'Capacity':<10}")
    print("-" * 130)

    # Виводимо інформацію для кожної події викладача
    for event in schedule:
        # Формуємо інформацію про групи, включаючи підгрупи, якщо вони є
        group_info = ', '.join([
            f"{gid}" + (
                f" (Subgroup {event.subgroup_ids[gid]})" if event.subgroup_ids and gid in event.subgroup_ids else ''
            )
            for gid in event.group_ids
        ])
        
        # Обчислюємо кількість студентів у події
        total_students = sum(
            groups[gid]['NumStudents'] // 2 if event.subgroup_ids and gid in event.subgroup_ids else
            groups[gid]['NumStudents']
            for gid in event.group_ids
        )
        
        # Отримуємо місткість аудиторії
        auditorium_capacity = auditoriums[event.auditorium_id]

        # Виводимо інформацію по колонках
        print(f"{event.timeslot:<25} {group_info:<30} {event.subject_name:<30} {event.event_type:<15} {event.lecturer_id:<10}"
              f"{event.auditorium_id:<10} {total_students:<10} {auditorium_capacity:<10}")

    print("-" * 130)
    print("Кінець розкладу\n")



# Головна функція для запуску генерації даних та алгоритму
def main():
    # Параметри для генерації даних
    num_groups = 4  # Кількість груп
    num_subjects_per_group = 3  # Кількість предметів на групу
    num_lecturers = 6  # Кількість викладачів
    num_auditoriums = 7  # Кількість аудиторій

    # Генеруємо випадкові дані
    groups = generate_random_groups(num_groups)  # Генеруємо групи
    subjects = generate_random_subjects(groups, num_subjects_per_group)  # Генеруємо предмети
    lecturers = generate_random_lecturers(num_lecturers, subjects)  # Генеруємо викладачів
    auditoriums = generate_random_auditoriums(num_auditoriums)  # Генеруємо аудиторії

    # Запускаємо генетичний алгоритм для створення розкладу
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