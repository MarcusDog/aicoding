package com.lidacollege.volunteer.common.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;
import javax.crypto.SecretKey;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class JwtTokenProvider {

    private final SecretKey secretKey;
    private final long expirationMinutes;

    public JwtTokenProvider(
        @Value("${app.jwt.secret}") String secret,
        @Value("${app.jwt.expiration-minutes}") long expirationMinutes
    ) {
        byte[] bytes = secret.getBytes(StandardCharsets.UTF_8);
        this.secretKey = bytes.length >= 32 ? Keys.hmacShaKeyFor(bytes) : Keys.hmacShaKeyFor(Decoders.BASE64.decode("dm9sdW50ZWVyLW1hbmFnZW1lbnQtc3lzdGVtLXNlY3JldC1rZXktMjAyNg=="));
        this.expirationMinutes = expirationMinutes;
    }

    public String generate(LoginUser loginUser) {
        Instant now = Instant.now();
        Instant expireAt = now.plusSeconds(expirationMinutes * 60);
        return Jwts.builder()
            .subject(String.valueOf(loginUser.getUserId()))
            .claim("username", loginUser.getUsername())
            .claim("roleCode", loginUser.getRoleCode())
            .claim("refId", loginUser.getRefId())
            .issuedAt(Date.from(now))
            .expiration(Date.from(expireAt))
            .signWith(secretKey)
            .compact();
    }

    public LoginUser parse(String token) {
        Claims claims = Jwts.parser()
            .verifyWith(secretKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();
        return LoginUser.builder()
            .userId(Long.valueOf(claims.getSubject()))
            .username(claims.get("username", String.class))
            .roleCode(claims.get("roleCode", String.class))
            .refId(Long.valueOf(String.valueOf(claims.get("refId"))))
            .build();
    }
}
