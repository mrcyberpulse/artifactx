import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";

import { AuthLayout } from "@/pages/auth/AuthLayout";
import { Label } from "@/components/ui/Label";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/features/auth/AuthContext";
import { ApiError } from "@/lib/api-client";
import { registerSchema, type RegisterFormValues } from "@/lib/validation";

export function RegisterPage() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({ resolver: zodResolver(registerSchema) });

  const onSubmit = async (values: RegisterFormValues) => {
    setServerError(null);
    try {
      await registerUser(values.email, values.fullName, values.password);
      navigate("/", { replace: true });
    } catch (err) {
      setServerError(
        err instanceof ApiError ? err.message : "Unable to create your account. Please try again.",
      );
    }
  };

  return (
    <AuthLayout title="Create your account" subtitle="Software Supply Chain Security Platform">
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <div>
          <Label htmlFor="fullName">Full name</Label>
          <Input id="fullName" autoComplete="name" {...register("fullName")} />
          {errors.fullName && <p className="mt-1 text-xs text-danger">{errors.fullName.message}</p>}
        </div>
        <div>
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
          {errors.email && <p className="mt-1 text-xs text-danger">{errors.email.message}</p>}
        </div>
        <div>
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" autoComplete="new-password" {...register("password")} />
          {errors.password && <p className="mt-1 text-xs text-danger">{errors.password.message}</p>}
          <p className="mt-1 text-xs text-muted">At least 12 characters, with a letter and a digit.</p>
        </div>
        {serverError && <p className="text-sm text-danger" role="alert">{serverError}</p>}
        <Button type="submit" className="w-full" isLoading={isSubmitting}>
          Create account
        </Button>
      </form>
      <p className="mt-5 text-center text-sm text-muted">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-accent hover:underline">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
