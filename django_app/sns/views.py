from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Message,Friend,Group,Good
from .forms import GroupCheckForm,GroupSelectForm,\
  FriendsForm,CreateGroupForm,PostForm


#indexのレビュー関数
@login_required(login_url='/admin/login/')
def index(request, page=1):
  #publicのユーザーを取得
  (public_user, public_group) = get_public()

  #POST送信時ｎ処理
  if request.method == 'POST':

    #groupのチェックを更新したいときの処理
    #フォームの用意
    checkform = GroupCheckForm(request.user,request.POST)
    #チェックされたgroup名リストにまとめる
    glist = []
    for item in request.POST.getlist('groups'):
      glist.append(item)
    #messageの取得
    messages = get_your_group_message(request.user, \
      glist, page)

  #getアクセス時の処理
  else:
    #フォームの用意
    checkform = GroupCheckForm(request.user)
    #groupのリストを取得
    gps = Group.objects.filter(owner=request.user)
    glist = [public_group.title]
    for item in gps:
      glist.append(item.title)
    #メッセージの取得
    messages = get_your_group_message(request.user, glist, page)

    #共通処理
  params = {
    'login_user':request.user,
    'contents':messages,
    'check_form':checkform,
  }
  return render(request, 'sns/index.html', params)

@login_required(login_url='/admin/login/')
def groups(request):
  #自分が登録したFriendを取得
  friends = Friend.objects.filter(owner=request.user)

  #POST送信時の処理
  if request.method == 'POST':

    #GROUPメニュー選択じの処理
    if request.POST['mode'] == '__groups_form__':
      #選択したグループ名の取得
      sel_group = request.POST['groups']
      #GROUPを取得
      gp = Group.objects.filter(owner=request.user) \
        .filter(title=sel_group).first()
      #GROUPに含まれるFRIENDの取得
      fds = Friend.objects.filter(owner=request.user) \
        .filter(group=gp)
      print(Friend.objects.filter(owner=request.user))
      #FRIENDのユーザーをリストにまとめる
      vlist = []
      for item in fds:
        vlist.append(item.user.username)
      #フォームの用意
      groupsform = GroupSelectForm(request.user,request.POST)
      friendsform = FriendsForm(request.user, \
        friends=friends, vals=vlist)


    #FRIENｓのチェック時の処理
    if request.POST['mode'] == '__friends_form__':
      #選択したGROUPの取得
      sel_group = request.POST=['group']
      group_obj = Group.objects.filter(titlle=sel_group).first()
      print(group_obj)
      #チェックしたFRIENDsを取得
      sel_fds = request.POST.getlist('friends')
      #FRIENDsのUsERを取得
      sel_users = User.objects.filter(username__in=sel_fds)
      #Userのリストに含まれるユーザーが登録したFRIENDを取得
      fds = Friend.objects.filter(owner=request.user) \
        .filter(user__in=sel_users)
      #全てのFRIENDにGROUPを設定し保存
      vlist = []
      for item in fds:
        item.group = group_obj
        item.save()
        vlist.append(item.user.username)
      #メッセージ設定
      messages.success(request, ' チェックされたFriendを' + \
        sel_group + 'に登録しました。')
      #フォーム用意
      groupsform = GroupSelectForm(request.user, \
        {'groups':sel_group})
      friendsform = FriendsForm(request.user, \
        friends=friends, vals=vlist)


  #GETアクセス時んぼ処理
  else:
    #フォームの用意
    groupsform = GroupSelectForm(request.user)
    friendsform = FriendsForm(request.user, friends=friends, \
      vals=[])
    sel_group = '-'
  #共通処理
  createform = CreateGroupForm()
  params = {
    'login_user':request.user,
    'groups_form':groupsform,
    'friends_form':friendsform,
    'create_form':createform,
    'group':sel_group,
  }
  return render(request, 'sns/groups.html', params)


#FRIENDの追加処理
@login_required(login_url='/admin/login/')
def  add(request):
  #追加するUser取得
  add_name = request.GET['name']
  add_user = User.objects.filter(username=add_name).first()
  #Userが本人のときの処理
  if add_user == request.user:
    messages.info(request, "自分自身をFriendに追加することは\
      出来ません。")
    return redirect(to='/sns')

  #PUblicの取得
  (public_user, public_group) = get_public()
  #add-userのFRIENDの数を調べる
  frd_num = Friend.objects.filter(owner=request.user) \
    .filter(user=add_user).count()
  #ゼロより大きければ登録済み
  if frd_num > 0:
    messages.info(request, add_user.username + \
      ' は既に追加されています。')
    return redirect(to='/sns')
  
  #ここからFRIENDの登録処理
  frd = Friend()
  frd.owner = request.user
  frd.user = add_user
  frd.group = public_group
  frd.save()
  #メッセージ設定
  messages.success(request, add_user.username + ' を追加しました！\
    groupページに移動して、追加したFriendをメンバーに設定してください。')
  return redirect(to='/sns')
#グループ作成処理
@login_required(login_url='/admin/login/')
def creategroup(request):
  #GROUPを作り、Userとtitleを設定して保存
  gp = Group()
  gp.owner = request.user
  gp.title = request.user.username + 'の' + request.POST['group_name']
  gp.save()
  messages.info(request, '新しいグループを作成しました。')
  return redirect(to='/sns/groups')


#メッセージポスト処理
@login_required(login_url='/admin/login/')
def post(request):
  #POST送信処理
  if request.method == 'POST':
    #送信内容の取得
    gr_name = request.POST['groups']
    content = request.POST['content']
    #groupの取得
    group = Group.objects.filter(owner=request.user) \
      .filter(title=gr_name).first()
    if group == None:
      (pub_user, group) = get_public()
    #messageを作成し設定して保存
    msg = Message()
    msg.owner = request.user
    msg.group = group
    msg.content = content
    msg.save()
    #メッセージ設定
    messages.success(request, '新しいメッセージを投稿しました。')
    return redirect(to='/sns')

  #GETアクセス時の処理
  else:
    form = PostForm(request.user)

  #共通処理
  params = {
    'login_user':request.user,
    'form':form,
  }
  return render(request, 'sns/post.html', params)

#投稿シェア
@login_required(login_url='/admin/login/')
def share(request, share_id):
  #シェアするメッセージの取得
  share = Message.objects.get(id=share_id)
  print(share)
  #POST送信時処理
  if request.method == 'POST':
    #送信内容取得
    gr_name = request.POST['groups']
    content = request.POST['content']
    #Group取得
    group = Group.objects.filter(owner=request.user) \
      .filter(title=gr_name).first()
    if group == None:
      (pub_user, group) = get_public()
    #メッセージを作成して設定
    msg = Message()
    msg.owner = request.user
    msg.group = group
    msg.content = content
    msg.share_id = share_id
    msg.save()
    share_msg = msg.get_share()
    share_msg.share_count += 1
    share_msg.save()
    #メッセージ設定
    messages.success(request, 'メッセージをシェアしました。')
    return redirect(to='/sns')

  #共通処理
  form = PostForm(request.user)
  params = {
    'login_user':request.user,
    'form':form,
    'share':share,
  }
  return render(request, 'sns/share.html', params)

#goodボタン処理
@login_required(login_url='/admin/login/')
def good(request, good_id):
  #goodするmessageを取得
  good_msg = Message.objects.get(id=good_id)
  #自分がメッセージにgoodした数を調べる
  is_good = Good.objects.filter(owner=request.user) \
    .filter(message=good_msg).count()
  #ゼロより大きければ既にgood済み
  if is_good > 0:
    messages.success(request, '既にメッセージにはgoodしています')
    return redirect(to='/sns')

  #messageのgoodCOUNTを１増やす
  good_msg.good_count +=1
  good_msg.save()
  #good作成し設定して保存
  good = Good()
  good.owner = request.user
  good.message = good_msg
  good.save()
  #メッセージ設定
  messages.success(request, 'メッセージにgoodしました。')
  return redirect(to='/sns')


#指定されたグループおよび検索文字によるmessageの取得
def get_your_group_message(owner, glist, page):
  page_num = 10 #ページあたりの表示数
  #PUblicの取得
  (public_user,public_group) = get_public()
  #チェックされたgroupの取得
  groups = Group.objects.filter(Q(owner=owner) \
    |Q(owner=public_user)).filter(title__in=glist)
  #groupに含まれるFRIENDの取得
  me_friends = Friend.objects.filter(group__in=groups)
  #FriendのUserをリストにまとめる
  me_users = []
  for f in me_friends:
    me_users.append(f.user)
  #UserのUserが作ったgroupの取得
  his_groups = Group.objects.filter(owner__in=me_users)
  his_friends = Friend.objects.filter(user=owner) \
    .filter(group__in=his_groups)
  me_groups = []
  for hf in his_friends:
    me_groups.append(hf.group)
  #groupがgroupsに含まれるか、me-groupsに含まれる
  messages = Message.objects.filter(Q(group__in=groups) \
    |Q(group__in=me_groups))
  #ページネーションで指定ページを取得
  page_item = Paginator(messages, page_num)
  return page_item.get_page(page)

#PUblicなUserとgroupを取得
def get_public():
  public_user = User.objects.filter(username='public').first()
  public_group = Group.objects.filter \
    (owner=public_user).first()
  return (public_user, public_group)


