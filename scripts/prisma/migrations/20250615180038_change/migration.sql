/*
  Warnings:

  - You are about to drop the `Element` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Feedback` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Step` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Thread` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `User` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "Element" DROP CONSTRAINT "Element_stepId_fkey";

-- DropForeignKey
ALTER TABLE "Element" DROP CONSTRAINT "Element_threadId_fkey";

-- DropForeignKey
ALTER TABLE "Feedback" DROP CONSTRAINT "Feedback_stepId_fkey";

-- DropForeignKey
ALTER TABLE "Step" DROP CONSTRAINT "Step_parentId_fkey";

-- DropForeignKey
ALTER TABLE "Step" DROP CONSTRAINT "Step_threadId_fkey";

-- DropForeignKey
ALTER TABLE "Subscription" DROP CONSTRAINT "Subscription_userId_fkey";

-- DropForeignKey
ALTER TABLE "Thread" DROP CONSTRAINT "Thread_userId_fkey";

-- DropTable
DROP TABLE "Element";

-- DropTable
DROP TABLE "Feedback";

-- DropTable
DROP TABLE "Step";

-- DropTable
DROP TABLE "Thread";

-- DropTable
DROP TABLE "User";

-- CreateTable
CREATE TABLE "elements" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "threadId" TEXT,
    "stepId" TEXT NOT NULL,
    "metadata" JSONB NOT NULL,
    "mime" TEXT,
    "name" TEXT NOT NULL,
    "objectKey" TEXT,
    "url" TEXT,
    "chainlitKey" TEXT,
    "display" TEXT,
    "size" TEXT,
    "language" TEXT,
    "page" INTEGER,
    "props" JSONB,

    CONSTRAINT "elements_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSONB NOT NULL,
    "identifier" TEXT NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "feedbacks" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "stepId" TEXT,
    "name" TEXT NOT NULL,
    "value" DOUBLE PRECISION NOT NULL,
    "comment" TEXT,

    CONSTRAINT "feedbacks_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "steps" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "parentId" TEXT,
    "threadId" TEXT,
    "input" TEXT,
    "metadata" JSONB NOT NULL,
    "name" TEXT,
    "output" TEXT,
    "type" "StepType" NOT NULL,
    "showInput" TEXT DEFAULT 'json',
    "isError" BOOLEAN DEFAULT false,
    "startTime" TIMESTAMP(3) NOT NULL,
    "endTime" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "steps_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "threads" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deletedAt" TIMESTAMP(3),
    "name" TEXT,
    "metadata" JSONB NOT NULL,
    "tags" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "userId" TEXT,

    CONSTRAINT "threads_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "elements_stepId_idx" ON "elements"("stepId");

-- CreateIndex
CREATE INDEX "elements_threadId_idx" ON "elements"("threadId");

-- CreateIndex
CREATE INDEX "users_identifier_idx" ON "users"("identifier");

-- CreateIndex
CREATE UNIQUE INDEX "users_identifier_key" ON "users"("identifier");

-- CreateIndex
CREATE INDEX "feedbacks_createdAt_idx" ON "feedbacks"("createdAt");

-- CreateIndex
CREATE INDEX "feedbacks_name_idx" ON "feedbacks"("name");

-- CreateIndex
CREATE INDEX "feedbacks_stepId_idx" ON "feedbacks"("stepId");

-- CreateIndex
CREATE INDEX "feedbacks_value_idx" ON "feedbacks"("value");

-- CreateIndex
CREATE INDEX "feedbacks_name_value_idx" ON "feedbacks"("name", "value");

-- CreateIndex
CREATE INDEX "steps_createdAt_idx" ON "steps"("createdAt");

-- CreateIndex
CREATE INDEX "steps_endTime_idx" ON "steps"("endTime");

-- CreateIndex
CREATE INDEX "steps_parentId_idx" ON "steps"("parentId");

-- CreateIndex
CREATE INDEX "steps_startTime_idx" ON "steps"("startTime");

-- CreateIndex
CREATE INDEX "steps_threadId_idx" ON "steps"("threadId");

-- CreateIndex
CREATE INDEX "steps_type_idx" ON "steps"("type");

-- CreateIndex
CREATE INDEX "steps_name_idx" ON "steps"("name");

-- CreateIndex
CREATE INDEX "steps_threadId_startTime_endTime_idx" ON "steps"("threadId", "startTime", "endTime");

-- CreateIndex
CREATE INDEX "threads_createdAt_idx" ON "threads"("createdAt");

-- CreateIndex
CREATE INDEX "threads_name_idx" ON "threads"("name");

-- AddForeignKey
ALTER TABLE "elements" ADD CONSTRAINT "elements_stepId_fkey" FOREIGN KEY ("stepId") REFERENCES "steps"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "elements" ADD CONSTRAINT "elements_threadId_fkey" FOREIGN KEY ("threadId") REFERENCES "threads"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "feedbacks" ADD CONSTRAINT "feedbacks_stepId_fkey" FOREIGN KEY ("stepId") REFERENCES "steps"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "steps" ADD CONSTRAINT "steps_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "steps"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "steps" ADD CONSTRAINT "steps_threadId_fkey" FOREIGN KEY ("threadId") REFERENCES "threads"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "threads" ADD CONSTRAINT "threads_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Subscription" ADD CONSTRAINT "Subscription_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
