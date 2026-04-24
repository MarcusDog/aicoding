package com.lidacollege.volunteer.modules.auth.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.lidacollege.volunteer.common.exception.BusinessException;
import com.lidacollege.volunteer.common.security.JwtTokenProvider;
import com.lidacollege.volunteer.common.security.LoginUser;
import com.lidacollege.volunteer.common.security.SecurityHelper;
import com.lidacollege.volunteer.common.util.PasswordUtils;
import com.lidacollege.volunteer.modules.auth.dto.LoginRequest;
import com.lidacollege.volunteer.modules.system.entity.AdminUser;
import com.lidacollege.volunteer.modules.system.entity.Student;
import com.lidacollege.volunteer.modules.system.entity.SysUser;
import com.lidacollege.volunteer.modules.system.mapper.AdminUserMapper;
import com.lidacollege.volunteer.modules.system.mapper.StudentMapper;
import com.lidacollege.volunteer.modules.system.mapper.SysUserMapper;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final SysUserMapper sysUserMapper;
    private final StudentMapper studentMapper;
    private final AdminUserMapper adminUserMapper;
    private final JwtTokenProvider jwtTokenProvider;

    public Map<String, Object> login(LoginRequest request) {
        SysUser sysUser = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>()
            .eq(SysUser::getUsername, request.username())
            .eq(SysUser::getAccountStatus, "ENABLED"));
        if (sysUser == null || !PasswordUtils.matches(request.password(), sysUser.getPasswordHash())) {
            throw new BusinessException("用户名或密码错误");
        }
        sysUser.setLastLoginTime(LocalDateTime.now());
        sysUser.setUpdatedAt(LocalDateTime.now());
        sysUserMapper.updateById(sysUser);

        LoginUser loginUser = LoginUser.builder()
            .userId(sysUser.getId())
            .username(sysUser.getUsername())
            .roleCode(sysUser.getRoleCode())
            .refId(sysUser.getRefId())
            .build();

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("token", jwtTokenProvider.generate(loginUser));
        result.put("user", buildUserProfile(sysUser));
        return result;
    }

    public Map<String, Object> currentUser() {
        LoginUser loginUser = SecurityHelper.currentUser();
        SysUser sysUser = sysUserMapper.selectById(loginUser.getUserId());
        if (sysUser == null) {
            throw new BusinessException("用户不存在");
        }
        return buildUserProfile(sysUser);
    }

    private Map<String, Object> buildUserProfile(SysUser sysUser) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("userId", sysUser.getId());
        result.put("username", sysUser.getUsername());
        result.put("roleCode", sysUser.getRoleCode());
        result.put("refId", sysUser.getRefId());
        if ("STUDENT".equals(sysUser.getRoleCode())) {
            Student student = studentMapper.selectById(sysUser.getRefId());
            result.put("displayName", student == null ? sysUser.getUsername() : student.getName());
            result.put("collegeName", student == null ? null : student.getCollegeName());
        } else {
            AdminUser adminUser = adminUserMapper.selectById(sysUser.getRefId());
            result.put("displayName", adminUser == null ? sysUser.getUsername() : adminUser.getName());
            result.put("collegeName", "数字科学学院");
        }
        return result;
    }
}
