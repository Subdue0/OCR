import os
import json
import requests
from PIL import Image
data_file = 'checkcode.json'








	
'''
数据分析：

经过大量的观察推理，验证码图片中不包含o（出现极少，视为不存在），z（从未出现），9（从未出现）这三个字符，
猜测o与0，z与2，9与g太像了，所以为了方便用户识别就去掉了这三个字符，很不幸的是，虽然去掉了这三个非常相像的，
但还是存在两种比较相像的情况，比如i，j，l，1和0,8,6。对这两种情况，已经不适用普遍的匹配规则了，所以需要特殊处理，
代码采用了取相像数字最大相似度的最大值的办法，确定最终的验证码（key）


普遍匹配规则：

先看前三个二进制值的相似度，如果都小于190，就直接跳过key，
如果有一个大于等于190的，就遍历整个列表找250及以上同时记录230以上的个数，如果找到就停止遍历，确定验证码（key）；
如果没有250及以上的，就看230以上有多少个，如果3个及以上就确定验证码（key）


特殊匹配规则（适用于i，j，l，1和0,8,6）：

i，j，l，1（0,8,6）中任何一个验证码在使用普遍匹配规则的时候，
遍历到i的时候，先看前三个二进制值的相似度，如果有一个大于等于200，就找i，j，l，1（0,8,6）每个字符中的最大相似度，
然后比较这几个字符中的最大相似度的最大值，也就是最终的验证码（key）
'''
# similarity为相似度，输出相似度similarity=264即是数据字典文件中的数据和验证码二进制值一模一样
	
	
def first_distinguish_single_checkcode(load_dict, single_checkcode_value):
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
			if each_letter == ord('o') or each_letter == ord('z') or each_letter == ord('9'):
					continue
			# 测试数据	
			# print('\n')
			# print('上图与字典数据文件的'+chr(each_letter)+'的比较')
			for each_key_value in range(len(load_dict[chr(each_letter)])):
				for each_key_value_bit in range(264):
					if single_checkcode_value[each_key_value_bit] == load_dict[chr(each_letter)][each_key_value][each_key_value_bit]:
						similarity += 1
				# 测试数据
				# print('第'+(str(each_key_value+1))+'条数据相似度：'+str(similarity))
				if similarity > 255:
					if chr(each_letter) != 'i' and chr(each_letter) != 'l' and chr(each_letter) != 'h' and chr(each_letter) != 'n':
						print('验证码'+chr(each_letter)+'已经被识别出来')
						return chr(each_letter)
				if similarity > single_letter_max_similarity:
					single_letter_max_similarity = similarity
				# 重点，比较完后必须清零，否则影响后面的比较
				similarity = 0
			# 将最大的相似度存进字典中
			dict_max_similarity[chr(each_letter)] = single_letter_max_similarity
			single_letter_max_similarity = 0
	# 找出字典中的最大相似度的key
	single_checkcode = max(dict_max_similarity, key=dict_max_similarity.get)
	# 查看字母的所有数据相似度
	print(dict_max_similarity)
	dict_max_similarity = {}
	print('验证码'+single_checkcode+'已经被识别出来')
	return single_checkcode



if __name__=='__main__':
	img_num = 3000
	
	
	if os.path.exists('./image/') == False:
		os.makedirs('./image/', exist_ok=True)
		image_url = "http://10.20.208.12/(3vnntcya1lnohu45athqjt3a)/CheckCode.aspx??"
		for img_name in range(img_num):
			r = requests.get(image_url)
			with open('./image/'+str(img_name+1)+'.png', 'wb') as f:
				f.write(r.content)
	
	
	try:
		with open(data_file,'r') as load_f:
			load_dict = json.load(load_f)
			print('读取数据完成...')
	except:
		print('无法读取数据文件的内容，检查当前目录的'+data_file+'是否存在，文件中的内容至少为空字典。')
		exit(-1)


	list_checkcode = []
	for test in range(img_num):
		img = Image.open('./image/'+str(test+1)+'.png')
	# img = Image.open('./image/'+'1'+'.png')
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
			for y in range(0,22):
				for x in range(position[start],position[end]):
					print(photo.getpixel((x,y)),end='')
				print()
			# 获取验证码的二进制值
			single_checkcode_value = ''
			for y in range(0, 22):
				for x in range(position[start],position[end]):
					single_checkcode_value+=str(photo.getpixel((x,y)))
			checkcode += first_distinguish_single_checkcode(load_dict, single_checkcode_value)
		print('****************************************')
		print('验证码为：'+checkcode)
		print('****************************************')
		list_checkcode.append(checkcode)
	print(list_checkcode)
	for i in range(img_num):
		# 有样板才执行
		if os.path.exists('./image/'+str(i+1)+'.png') == True:
			# 相关图片不存在才会重命名
			if os.path.exists('./image/'+list_checkcode[i]+'.png') == False:
				os.rename('./image/'+str(i+1)+'.png', './image/'+list_checkcode[i]+'.png')
			else:
				os.remove('./image/'+str(i+1)+'.png')
