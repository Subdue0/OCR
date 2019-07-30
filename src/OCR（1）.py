import os
import sys
import json
import requests
from PIL import Image



	
'''
意图：
验证码的识别，是设计正方教务系统抢课软件的必备条件。


识别效果：
经过大量验证码的训练识别，识别的正确率已经有99%。


识别的对象：
正方教务系统登录界面的验证码



验证码分析：

经过大量的观察推理，验证码图片中是以26个字母和10个数字的随机4个组成的，一共有36个字符，但是不包含o（出现极少，视为不存在），z（从未出现），9（从未出现）这三个字符，最终就只有34个字符，猜测o与0，z与2，9与g太像了，所以设计者为了方便用户识别就去掉了这三个字符。


识别思路：

我收集了很多样本数据，它们存在字典数据文件中，用来识别匹配验证码，一张验证码图片为四个部分，分别是（5，17）, （17，29），（29，41），（41，53），
每一个部分就是一个验证码。每一个部分的验证码的像素点一共有264个。从第一个验证码开始，我把要识别的验证码和我数据字典中的每个字母的每一条样本数据
进行比较，寻找大于255相似度（最大相似度：264）的那条数据，同时记录每个字符的最大相似度，一旦找到就直接返回这条数据的key（验证码）。如果遍历完
所有字符都找不到大于255相似度，就以所有字符的最大相似度的最大值的key作为验证码，因为它是所有字母里面相似度最高的。


特殊处理：

比如i，j和h，n。对这两组，我强制比较它们的最大相似度，而不是遇到相似度极高的，直接匹配。
'''	
	
def recognize_single_checkcode(load_dict, single_checkcode_value, which_one):
	similarity = 0
	sum_similarity = 0
	avg_sum_similarity = 0
	dict_max_similarity = {}
	single_letter_max_similarity = similarity
	single_checkcode = [ord('a'),ord('z'),   ord('0'),ord('9')]
	# 遍历每一个验证码
	for each_range_start in range(0, 3, 2):
		start = each_range_start
		end = each_range_start+1
		# 遍历所有字母和数字
		for each_letter in range(single_checkcode[start], single_checkcode[end]):
			# 去掉几个不存在的验证码
			if each_letter == ord('o') or each_letter == ord('z') or each_letter == ord('9'):
					continue
			# 调试信息，查看遍历到什么什么字母了
			try:
				if sys.argv[1] == 'log':
					print()
					print('第'+which_one+'位验证码与字典数据文件的'+chr(each_letter)+'的比较')
			except:
				pass
			# 遍历所有字符的所有数据，和验证码一一比对，得出相似度
			for each_key_value in range(len(load_dict[chr(each_letter)])):
				for each_key_value_bit in range(264):
					if single_checkcode_value[each_key_value_bit] == load_dict[chr(each_letter)][each_key_value][each_key_value_bit]:
						similarity += 1
				# 调试信息，输出验证码和每个字符的所有数据比较结果
				try:
					if sys.argv[1] == 'log':
						print('第'+(str(each_key_value+1))+'条数据相似度：'+str(similarity))
				except:
					pass
				# 大于255直接输出验证码，但是i，l和h，n除外
				if similarity > 255:
					if chr(each_letter) != 'i' and chr(each_letter) != 'l' and chr(each_letter) != 'h' and chr(each_letter) != 'n':
						# 调试信息
						try:
							if sys.argv[1] == 'log':
								print('\n')
								print('********************************************')
								print('验证码相似度为：'+str(similarity)+'，验证码'+chr(each_letter)+'已经被识别出来')
								print('********************************************')
								print('\n')
						except:
							pass
						return chr(each_letter)
				# 存取每个字符的最大相似度
				if similarity > single_letter_max_similarity:
					single_letter_max_similarity = similarity
				# 重点，比较完后必须清零，否则影响后面的比较
				similarity = 0
			# 将最大的相似度存进字典中
			dict_max_similarity[chr(each_letter)] = single_letter_max_similarity
			single_letter_max_similarity = 0
	# 找出字典中的最大相似度的key
	single_checkcode = max(dict_max_similarity, key=dict_max_similarity.get)
	# 调试信息，输出所有字符的最大相似度字典
	try:
		if sys.argv[1] == 'log':
			print('\n')
			print(dict_max_similarity)
	except:
		pass
	dict_max_similarity = {}
	# 调试信息，输出每个验证码的识别结果
	try:
		if sys.argv[1] == 'log':
			print('\n')
			print('********************************************')
			print('通过比较最大相似度，验证码'+single_checkcode+'已经被识别出来')
			print('********************************************')
			print('\n')
	except:
		pass
	return single_checkcode


def recognize_checkcode(data_file, image):
	# try:
	with open(data_file, 'r') as load_f:
		load_dict = json.load(load_f)
		# 调试信息
		try:
			if sys.argv[1] == 'log':
				print('读取数据完成...')
		except:
			pass
	# except:
		# 报错，无法正常读取数据。
		# print('无法读取数据文件的内容，检查当前目录的'+data_file+'是否存在，文件中的内容至少为空字典。')
		# exit(-1)
		
	img = Image.open(image)
	Img = img.convert('L')
	threshold = 25
	table = []
	for i in range(256):
		if i < threshold:
			table.append(0)
		else:
			table.append(1)
	photo = Img.point(table, '1')
	
	
	



	checkcode = ''
	position = [5,17,   17,29,   29,41,   41,53]
	for each_range_start in range(0,7,2):
		start = each_range_start
		end = each_range_start+1
		# 调试信息，输出识别的单个验证码
		try:
			if sys.argv[1] == 'log':
				for y in range(0,22):
					for x in range(position[start],position[end]):
						print(photo.getpixel((x,y)),end='')
					print()
		except:
			pass
		# 获取验证码的二进制值
		single_checkcode_value = ''
		for y in range(0, 22):
			for x in range(position[start],position[end]):
				single_checkcode_value+=str(photo.getpixel((x,y)))
		# 计算正在遍历的是验证码中的哪一个
		which_one = '%.0f' %(start/2+1)
		checkcode += recognize_single_checkcode(load_dict, single_checkcode_value, which_one)	
	print('*******************')
	print('所有验证码为：'+checkcode)
	print('*******************')



if __name__=='__main__':
	image = '1.png'
	data_file = 'checkcode.json'
	recognize_checkcode(data_file, image)
