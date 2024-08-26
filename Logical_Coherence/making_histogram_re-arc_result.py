import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

base_dir = 'result/[CoT-re-arc_correct]result_'
save_dir = 'result/re-arc-figures'

df_concat = pd.DataFrame()

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for num_iter in range(0,5):
    df = pd.DataFrame()
    cot_file_name = f'[refine]cot_predict{num_iter}'
    cot_dir_path = base_dir + f'{num_iter}/'

    cot_result = pd.read_csv(cot_dir_path + cot_file_name+'.csv', converters={"code": lambda x: str(x)})

    df = pd.concat([df, cot_result])
    df_concat = pd.concat([df_concat, cot_result])

    df_sorted = df.sort_values(by=['task_id', 'correct_flag', 'try'],ascending=[True, False, True])
    series_accuracy = df_sorted.groupby('task_id')['correct_flag'].mean()
    series_accuracy.to_csv(f'{cot_dir_path}/accuracy_each_task.csv')
    filtered_accuracy_0 = series_accuracy[(series_accuracy < 2)]
    filtered_accuracy_2_6 = series_accuracy[ (series_accuracy >= 0.2) & (series_accuracy < 0.6)]
    filtered_accuracy_0_6 = series_accuracy[ (series_accuracy >= 0.6)]
    filtered_accuracy_0.to_csv(f'{cot_dir_path}/[accuracy_2]_each_task.csv')
    filtered_accuracy_0_6.to_csv(f'{cot_dir_path}/[accuracy_6]_each_task.csv')
    filtered_accuracy_2_6.to_csv(f'{cot_dir_path}/[accuracy_2_6]_each_task.csv')

df_sorted = df_concat.sort_values(by=['task_id', 'correct_flag', 'try'], ascending=[True, False, True])

# task_id별로 정확도를 계산합니다.
series_accuracy = df_sorted.groupby('task_id')['correct_flag'].mean()
series_accuracy.to_csv(f'result/accuracy_each_task.csv')

accuracy_counts = series_accuracy.value_counts().sort_index()
accuracy_counts.to_csv(f'result/tasks_by_accuracy.csv')

# 정확도에 따른 필터링을 수행하고 결과를 저장합니다.
filtered_accuracy_0 = series_accuracy[(series_accuracy < 2)]
filtered_accuracy_2_6 = series_accuracy[(series_accuracy >= 0.2) & (series_accuracy < 0.6)]
filtered_accuracy_0_6 = series_accuracy[(series_accuracy >= 0.6)]
filtered_accuracy_0.to_csv(f'result/[accuracy_2]_each_task.csv')
filtered_accuracy_0_6.to_csv(f'result/[accuracy_6]_each_task.csv')
filtered_accuracy_2_6.to_csv(f'result/[accuracy_2_6]_each_task.csv')

total_x_values = range(0, 101)
total_y_values = []

for num_iter in range(0,5):
    df_concat = pd.DataFrame()
    cot_file_name = f'[refine]cot_predict{num_iter}'
    cot_dir_path = base_dir + f'{num_iter}/'

    cot_result = pd.read_csv(cot_dir_path + cot_file_name+'.csv', converters={"code": lambda x: str(x)})

    df_concat = pd.concat([df_concat, cot_result])

    df_sorted = df_concat.sort_values(by=['task_id', 'correct_flag', 'try'], ascending=[True, False, True])

    unique_tasks = df_sorted['task_id'].unique()
    x_values = range(0, 101)
    y_values = [len(unique_tasks)]
    task_ids_list = [unique_tasks]

    for x in range(1,101):
        count = 0
        temp_task = []
        for task in unique_tasks:
            # 각 task_id에 대해 correct_flag의 처음 x개의 값이 모두 True인지 확인합니다.
            if len(df_sorted[(df_sorted['task_id'] == task) & (df_sorted['correct_flag'] == True)]) >= x:
                # 앞에서 x개의 correct_flag가 모두 True인 경우 count를 증가시킵니다.
                if df_sorted[df_sorted['task_id'] == task]['correct_flag'].iloc[:x].all():
                    count += 1
                    temp_task.append(task)
        task_ids_list.append(temp_task)
        y_values.append(count)

    info = {
        'x_values': x_values,
        'y_values': y_values,
        'task_ids_list': task_ids_list
    }

    total_y_values.append(y_values)

    df_info = pd.DataFrame(info)
    df_info.to_csv(f'{cot_dir_path}/[iter_{num_iter}]num_tasks_with_consecutive_correct_answers.csv', index=False)


total_info = {
        'x_values': total_x_values,
        'y_values': np.array(total_y_values).mean(axis=0).tolist(),
}

df_info = pd.DataFrame(total_info)
df_info.to_csv(f'result/num_tasks_with_consecutive_correct_answers.csv', index=False)

plt.figure(figsize=(10, 6))
plt.plot(x_values, y_values, linestyle='-') # marker='o'
plt.xlabel('Number of Consecutive Correct Answers (x)')
plt.ylabel('Number of Tasks')
plt.title('Number of Tasks with Consecutive Correct Answers')
plt.xticks(np.arange(0, 101, step=10))  # x축을 0부터 100까지 표시
plt.xlim(0, 100)  # x축 최소값을 0으로 설정
plt.ylim(0, max(y_values) + 0.1)
plt.grid(True)
plt.savefig(f'result/num_tasks_with_consecutive_correct_answers.png', dpi=300)
# plt.show()


x2_values = range(0, 101)
average_y_values = np.zeros(len(x2_values))

for task in unique_tasks:
    df_task = df_concat[df_concat['task_id'] == task]
    task_y_values = [1]

    for x in range(0, 100):
        correct_answers = df_task['correct_flag'].iloc[:x].sum()
        accuracy = (correct_answers+1) / (x+1)  # 누적 정답률 계산
        task_y_values.append(accuracy)

    # 해당 task의 누적 정답률을 전체 평균에 더합니다.
    average_y_values += np.array(task_y_values)

# 모든 task에 대해 평균을 구합니다.
average_y_values /= len(unique_tasks)

# 결과를 시각화합니다.
plt.figure(figsize=(10, 6))
plt.plot(x2_values, average_y_values, linestyle='-')
plt.xlabel('Number of Attempts (x)')
plt.ylabel('Average Cumulative Accuracy')
plt.title('Average Cumulative Accuracy Across Multiple Tasks')
plt.xticks(np.arange(0, 101, step=10))  # x축을 1부터 100까지 표시
plt.xlim(1, 100)  # x축 최소값을 1로 설정
plt.ylim(0, 1)  # y축을 0에서 1 사이로 설정
plt.grid(True)

# 플롯을 파일로 저장합니다.
plt.savefig(f'{save_dir}/average_cumulative_accuracy_plot.png', dpi=300)  # 파일명과 해상도를 지정

# 플롯을 화면에 보여줍니다.
# plt.show()


for task_id in unique_tasks:
    x3_values = range(0, 101)
    y3_values = [1]
    for x in range(0, 100):
        # x개의 correct_flag 값 중에서 True의 비율을 계산합니다.
        correct_answers = df_concat[df_concat['task_id']==task_id]['correct_flag'].iloc[:x].sum()
        accuracy = (correct_answers+1) / (x+1)  # 정답 비율
        y3_values.append(accuracy)

    # 결과를 시각화합니다.
    plt.figure(figsize=(10, 6))
    plt.plot(x3_values, y3_values, linestyle='-')
    plt.xlabel('Number of Attempts (x)')
    plt.ylabel('Cumulative Accuracy')
    plt.title(f'Cumulative Accuracy for Task ID {task_id}')
    plt.xticks(np.arange(0, 101, step=10))  # x축을 1부터 100까지 표시
    plt.xlim(1, 100)  # x축 최소값을 1로 설정
    plt.ylim(0, 1)  # y축을 0에서 1 사이로 설정
    plt.grid(True)

    # 플롯을 파일로 저장합니다.
    plt.savefig(f'{save_dir}/cumulative_accuracy_plot_{task_id}.png', dpi=300)  # 파일명과 해상도를 지정

    # 플롯을 화면에 보여줍니다.
    # plt.show()

# x축 값과 y축 값으로 나누기
x4_values = accuracy_counts.index
y4_values = accuracy_counts.values

# 결과를 시각화합니다.
plt.figure(figsize=(10, 6))
plt.bar(x4_values, y4_values, width=0.01, align='center')  # 히스토그램을 그립니다.
plt.xlabel('Accuracy')
plt.ylabel('Number of Tasks')
plt.title('Number of Tasks by Accuracy')
plt.xlim(0, 1)  # 정확도는 0에서 1 사이이므로 x축을 0에서 1로 설정
plt.grid(True)

# 플롯을 파일로 저장합니다.
plt.savefig(f'{save_dir}/tasks_by_accuracy_plot.png', dpi=300)  # 파일명과 해상도를 지정

# 플롯을 화면에 보여줍니다.
# plt.show()