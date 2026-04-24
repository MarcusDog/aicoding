package com.lidacollege.volunteer.modules.system.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.lidacollege.volunteer.modules.system.entity.Student;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface StudentMapper extends BaseMapper<Student> {
}
