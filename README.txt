1) информацию стоит забирать из елементов, как только очередная порция элементов найдена, иначе, после скроллинга,
часть эллементов пропадает из DOM
2) wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "statistic__team"))) - необходимо вызывать ДО driver.get