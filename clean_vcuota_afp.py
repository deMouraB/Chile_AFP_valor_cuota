# written by Bernardo de Moura
# Last update: 2019 Aug

# Import packages
import pandas as pd
import numpy as np
import os
import csv

# path to project
project_path = 'YOUR_PROJECT_PATH'

# path to raw data folder
raw_path = os.path.join(project_path, 'raw')

# path to manipulated data folder
data_path = os.path.join(project_path, 'dat')

# list relevant AFPs + date 
AFPs = ['Fecha' , 'CAPITAL', 'CUPRUM', 'HABITAT', 'MODELO', 'PLANVITAL', 'PROVIDA']

for letter in ['A', 'B', 'C', 'D', 'E']:
	# path to csv file with dirty_matrix data
	csv_filename = 'vcf' + str(letter) + '2002-2020.csv'
	dirty_matrix = os.path.join(raw_path, csv_filename)

	# note that the csv file is not one matrix but a collection of matrices broken up by the
	# phrase 'Valores Confirmados'.
	# what we do here is get the now numbers for each 'Valores Confirmados' string.
	# this gives us the beguinning of each matrix. now we need to get the row number for the
	# last row of the last matrix. We are looking for a 'Valores Provisorios' string
	# note that we are not interested in the data bellow 'Valores Provisorios - Sujetos a Confirmacion'

	row_list = []
	with open(dirty_matrix, 'r') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			try:
				first_column = row[0]
			except IndexError:
				continue
			else:
				if first_column.strip() == 'Valores Confirmados': 
					row_list.append(reader.line_num)
				elif first_column.strip() == 'Valores Provisorios - Sujetos a Confirmacion':
					row_list.append(reader.line_num)


	# index of rows at start of each matrix
	mat_row_sta = row_list[0:len(row_list)-1]
	mat_row_sta = [rownum+2 for rownum in mat_row_sta]

	# index of rows at start of each matrix
	mat_row_end = row_list[1:len(row_list)]
	mat_row_end = [rownum-2 for rownum in mat_row_end]

	# create matrix that will track fondo A for all AFPs
	clean_matrix = pd.DataFrame(columns=AFPs)

	# 
	for i in range(len(mat_row_sta)):
		# create small matrix that will be appended to clean_matrix
		df = pd.read_csv(dirty_matrix,              
			index_col=False,
			skiprows=mat_row_sta[i]-1,
			nrows=mat_row_end[i]-mat_row_sta[i],
			sep=';')
		
		# get rid of first row
		df = df.iloc[1:]

		# get variable list = intersection between aforementioned list of wanted AFPs and AFPs present in this particular matrix
		vars = list(set(AFPs) & set(list(df.columns.values.tolist())))

		# reduce matrix to include only relevant variables
		df = df[vars]

		# append (aka concatenate, in pandas lingo) small dataframe to fondo A general dataframe
		clean_matrix = pd.concat([clean_matrix, df])
		del df


	# export
	exp_path = os.path.join(data_path, csv_filename) 
	clean_matrix.to_csv(exp_path, sep = ';', index=False)
	del clean_matrix
