# -*- Encoding: utf-8 -*-
import re
import os

from log4f import debug_logger

log = debug_logger('log/parser', 'parser')

ignore = {
    '15923760': u'商户不存在',
    '21411682': u'没有评分数据',
    '13775000': u'没有评分数据',
    }

comment_star_progs = [
    re.compile(r'-str(\d+)'),
    re.compile(r'-star(\d+)'),
    ]


comment_time_progs = [
    re.compile(r'<span class="time">(.*?)</span>'),
    ]

comment_entry_progs = [
    # class="content"
    re.compile(r'<p class="desc J-desc">(.+?)</p>', re.DOTALL),  # 长点评
    re.compile(r'<p class="desc">(.+?)</p>', re.DOTALL),  # 短点评
    # class="comment-entry"
    re.compile(r'<div class="J_extra-cont Hide">(.+?)</div>', re.DOTALL),  # 长点评
    re.compile(r'<div id="review_\d+_summary">(.+?)</div>', re.DOTALL),  # 短点评
    # class="comment-text"
    re.compile(r'<div class="desc J_brief-cont-long Hide">\s*(.+?)\s*</div>', re.DOTALL),  # 长点评
    re.compile(r'<div class="(?:desc )?J_brief-cont">\s*(.+?)\s*</div>', re.DOTALL),  # 长点评
    ]

comment_rec_progs = [
    re.compile(r'<dl class="recommend-info clearfix">(.*?)</dl>', re.DOTALL),  # class="content"
    re.compile(r'<div class="comment-recommend">(.*?)</div>', re.DOTALL),  # class="comment-text"
    re.compile(r'<div class="comment-unit">\s*<ul>\s*(.*\S)\s*</ul>\s*</div>', re.DOTALL),  # class="comment-entry"
    ]

user_id_progs = [
    re.compile(r'class="user-info">\s*<a.*?href="/member/(\d+)".*?>(.*?)</a>', re.DOTALL),
    re.compile(r'<p class="name">\s*<a.*?href="/member/(\d+)".*?>(.*?)</a>', re.DOTALL),
    ]

def parse(progs, content, id, name, log_not_match=True):
    for idx, p in enumerate(progs):
        m = p.findall(content)
        if m:
            if len(m) > 1:
                log.error('multi-match {} {}. prog-idx={}'.format(id, name, idx))
            return m[0].decode('utf8')

    if log_not_match:
        log.error('failed to match {} {}'.format(id, name))
    return None


def detect(content, ptn):
    return ptn.findall(content)


score0_prog = re.compile(r'<i class="icon star-from item J-star-from"></i>')


def has_score0_notes(content):
    return len(score0_prog.findall(content)) > 0


def has_rev(content):
    return len(re.compile(r'comment-list').findall(content)) > 0


rev_prog = re.compile(r'<li[^>]+id="rev_(\d+)"(.+?)<span class="time">(.*?)</span>.*?</li>', re.DOTALL)


def parse_shop_comment(content, sid):
    ret = rev_prog.findall(content)

    # if has_rev(content) and len(ret) == 0:
    #     print sid  # check if correct comment num parsed
    for rev_id, text, timestamp in ret:
        star = parse(comment_star_progs, text, '{}-{}'.format(sid, rev_id), 'comment star')
        entry = parse(comment_entry_progs, text, '{}-{}'.format(sid, rev_id), 'comment entry')
        recommend = parse(comment_rec_progs, text, '{}-{}'.format(sid, rev_id), 'comment recommend', log_not_match=False)
        uid = parse(user_id_progs, text, '{}-{}'.format(sid, rev_id), 'comment user')

    return ret


if __name__ == '__main__':
    pass
