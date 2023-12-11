import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.title('Тестовое задание')
uploaded_file = st.file_uploader("Пожалуйста, загрузите файл формата CSV", type=['csv'])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='cp1251', quoting=3)
        st.write('Первые 5 строк файла (до предобработки):')
        st.write(df.head(3))

        df.columns = df.columns.str.replace('"', '')
        df = df.applymap(lambda x: x.replace('"', '') if isinstance(x, str) else x)
        df[df.columns[0]] = df[df.columns[0]].astype(int)
        df.columns = ['Количество больничных дней', 'Возраст', 'Пол']

    
        age = st.number_input('Задайте параметр age (Возраст)', 
                               min_value=int(df['Возраст'].min()), max_value=int(df['Возраст'].max()), value=35)
        work_days = st.number_input('Задайте параметр work_days (Количество больничных дней)', 
                                     min_value=int(df['Количество больничных дней'].min()), max_value=int(df['Количество больничных дней'].max()), value=2)


        df_pie = df
        df_pie['dist'] = df_pie['Количество больничных дней'].apply(lambda x: f'Больше {work_days}' if x > work_days else f'Меньше или равно {work_days}')
        data_male = df_pie[df_pie['Пол'] == 'М']['dist'].value_counts()
        data_female = df_pie[df_pie['Пол'] == 'Ж']['dist'].value_counts()
        data_old = df_pie[df_pie['Возраст'] > age]['dist'].value_counts()
        data_young = df_pie[df_pie['Возраст'] <= age]['dist'].value_counts()

        st.write("Критерии проверки:\n- Уровень значимости (p-value) выбран равным 0.05.\n- Проверка гипотез проводится при помощи t-теста (t_stat).")

        st.write(f"ГИПОТЕЗА: Мужчины пропускают в течение года более {work_days} рабочих дней (work_days) по болезни значимо чаще женщин")
        df_male = df[(df['Пол'] == 'М') & (df['Количество больничных дней'] > work_days)]['Количество больничных дней']
        df_female = df[(df['Пол'] == 'Ж') & (df['Количество больничных дней'] > work_days)]['Количество больничных дней']
        t_stat, p_value = stats.ttest_ind(df_male, df_female, equal_var=False)
        if p_value < 0.05:
            st.write("Результат проверки: Различие в пропущенных днях по болезни для мужчин и женщин статистически значимо.")
        else:
            st.write("Результат проверки: Статистически значимого различия в пропущенных днях по болезни для мужчин и женщин не обнаружено.")

        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]], subplot_titles=['Мужчины', 'Женщины'])
        fig.add_trace(
            go.Pie(labels=data_male.index, values=data_male.values, sort=False, textfont_size=16), 1,1)
        fig.add_trace(
            go.Pie(labels=data_female.index, values=data_female.values, sort=False, textfont_size=16), 1,2)
        fig.update_traces(textposition='inside', textinfo='label', texttemplate="%{percent}",
                          hoverinfo="percent+label", hovertemplate="%{label} - %{value} сотрудников<br>%{percent:.1%}<extra></extra>")
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        fig.update_layout(
            legend=dict(
                title='Кол-во больничных дней',
                itemsizing='constant',
                font=dict(size=16)
            ),
            font=dict(size=24)
        )
        fig.layout.annotations[0].update(y=0.9, font = dict(size=22, family='Verdana'))
        fig.layout.annotations[1].update(y=0.9, font = dict(size=22, family='Verdana'))
        st.plotly_chart(fig)

        fig1 = px.histogram(df_pie, x="Количество больничных дней", color="Пол", barmode='group', 
                            title='Число сотрудников, взявших n количество больничных дней, по полу')
        fig1.update_layout(xaxis_title='Количество больничных дней', yaxis_title='Число сотрудников')
        st.plotly_chart(fig1)


        st.write(f"ГИПОТЕЗА: Работники старше {age} лет (age) пропускают в течение года более {work_days} рабочих дней (work_days) по болезни значимо чаще своих более молодых коллег")
        df_old = df[(df['Возраст'] > age) & (df['Количество больничных дней'] > work_days)]['Количество больничных дней']
        df_young = df[(df['Возраст'] <= age) & (df['Количество больничных дней'] > work_days)]['Количество больничных дней']
        t_stat, p_value = stats.ttest_ind(df_old, df_young, equal_var=False)
        if p_value < 0.05:
            st.write("Результат проверки: Различие в пропущенных днях по болезни для старших и младших коллег статистически значимо")
        else:
            st.write("Результат проверки: Статистически значимого различия в пропущенных днях по болезни для старших и младших коллег не обнаружено")

        fig2 = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]], subplot_titles=[f'{age}+ лет', f'До {age} лет'])
        fig2.add_trace(
            go.Pie(labels=data_old.index, values=data_old.values, sort=False, textfont_size=16), 1,1)
        fig2.add_trace(
            go.Pie(labels=data_young.index, values=data_young.values, sort=False, textfont_size=16), 1,2)
        fig2.update_traces(textposition='inside', textinfo='label', texttemplate="%{percent}",
                          hoverinfo="percent+label", hovertemplate="%{label} - %{value} сотрудников<br>%{percent:.1%}<extra></extra>")
        fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        fig2.update_layout(
            legend=dict(
            title = 'Кол-во больничных дней'),
            font=dict(size=24))
        fig2.layout.annotations[0].update(y=0.9, font = dict(size=22, family='Verdana'))
        fig2.layout.annotations[1].update(y=0.9, font = dict(size=22, family='Verdana'))
        st.plotly_chart(fig2)
        
        
        df_mean = df_pie.groupby(by = 'Возраст').agg({'Количество больничных дней':'mean'}).round(1).reset_index()
        df_count = df_pie.groupby(by='Возраст')['Пол'].count().reset_index().rename(columns={'Пол': 'Количество'})
        fig3 = px.bar(df_count, x='Возраст', y='Количество', 
                     title='Количественное распределение сотрудников по возрастам')
        fig3.update_layout(xaxis_title='Возраст', yaxis_title='Число сотрудников')
        st.plotly_chart(fig3)
        
        fig4 = px.bar(df_mean, x='Возраст', y='Количество больничных дней', 
                     title='Среднее количество больничных дней по возрасту')
        fig4.update_layout(xaxis_title='Возраст', yaxis_title='Среднее количество больничных дней')
        st.plotly_chart(fig4)

    except:
        st.write('Пожалуйста, проверьте корректность загружаемого файла и его кодировку.\n Файл должен быть формата CSV и иметь 3 колонки:\n "Количество больничных дней", "Пол" и "Возраст"')